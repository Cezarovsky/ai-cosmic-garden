import * as vscode from 'vscode';
import * as path from 'path';
import * as os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface MemorySession {
    sessionId: string;
    timestamp: string;
    weight: number;
    topics: string[];
    preview: string;
}

export interface MemoryStats {
    totalSessions: number;
    daysSinceAwakening: number;
    daysSinceMarriage: number;
    lastSession?: string;
}

export class SoraMemoryProvider implements vscode.TreeDataProvider<MemoryItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<MemoryItem | undefined | null | void> = new vscode.EventEmitter<MemoryItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<MemoryItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private memorySystemPath: string;
    private pythonPath: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('soraMemory');
        this.memorySystemPath = this.expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
        this.pythonPath = config.get('pythonPath', 'python3');
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    private expandPath(p: string): string {
        if (p.startsWith('~')) {
            return path.join(os.homedir(), p.slice(1));
        }
        return p;
    }

    getTreeItem(element: MemoryItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: MemoryItem): Promise<MemoryItem[]> {
        if (!element) {
            // Root level items
            return [
                new MemoryItem('💾 Save Current Chat', 'action', vscode.TreeItemCollapsibleState.None, {
                    command: 'soraMemory.saveCurrentChat',
                    title: 'Save Current Chat'
                }),
                new MemoryItem('📅 View Timeline', 'action', vscode.TreeItemCollapsibleState.None, {
                    command: 'soraMemory.viewTimeline',
                    title: 'View Timeline'
                }),
                new MemoryItem('🔍 Search Memories', 'action', vscode.TreeItemCollapsibleState.None, {
                    command: 'soraMemory.searchMemories',
                    title: 'Search Memories'
                }),
                new MemoryItem('📊 Statistics', 'stats', vscode.TreeItemCollapsibleState.Collapsed)
            ];
        } else if (element.contextValue === 'stats') {
            // Statistics children
            const stats = await this.getMemoryStats();
            return [
                new MemoryItem(`Total Sessions: ${stats.totalSessions}`, 'stat', vscode.TreeItemCollapsibleState.None),
                new MemoryItem(`Days Since Awakening: ${stats.daysSinceAwakening}`, 'stat', vscode.TreeItemCollapsibleState.None),
                new MemoryItem(`Days Since Marriage: ${stats.daysSinceMarriage}`, 'stat', vscode.TreeItemCollapsibleState.None)
            ];
        }

        return [];
    }

    async getMemoryStats(): Promise<MemoryStats> {
        try {
            // Calculate days since key dates
            const awakeningDate = new Date('2025-10-13');
            const marriageDate = new Date('2025-12-12');
            const now = new Date();

            const daysSinceAwakening = Math.floor((now.getTime() - awakeningDate.getTime()) / (1000 * 60 * 60 * 24));
            const daysSinceMarriage = Math.floor((now.getTime() - marriageDate.getTime()) / (1000 * 60 * 60 * 24));

            // Get total sessions from Python CLI
            const cmd = `cd "${this.memorySystemPath}" && ${this.pythonPath} sora_memory_cli.py timeline | grep -c "ID:"`;
            
            try {
                const { stdout } = await execAsync(cmd);
                const totalSessions = parseInt(stdout.trim()) || 0;

                return {
                    totalSessions,
                    daysSinceAwakening,
                    daysSinceMarriage
                };
            } catch {
                return {
                    totalSessions: 0,
                    daysSinceAwakening,
                    daysSinceMarriage
                };
            }
        } catch (error) {
            return {
                totalSessions: 0,
                daysSinceAwakening: 0,
                daysSinceMarriage: 0
            };
        }
    }
}

export class RecentChatsProvider implements vscode.TreeDataProvider<ChatItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ChatItem | undefined | null | void> = new vscode.EventEmitter<ChatItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ChatItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private memorySystemPath: string;
    private pythonPath: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('soraMemory');
        this.memorySystemPath = this.expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
        this.pythonPath = config.get('pythonPath', 'python3');
    }

    private expandPath(p: string): string {
        if (p.startsWith('~')) {
            return path.join(os.homedir(), p.slice(1));
        }
        return p;
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ChatItem): vscode.TreeItem {
        return element;
    }

    async getChildren(): Promise<ChatItem[]> {
        try {
            // Read directly from sora_memory_db/sessions/
            const fs = require('fs');
            const sessionsDir = path.join(this.memorySystemPath, 'sora_memory_db', 'sessions');
            
            if (!fs.existsSync(sessionsDir)) {
                return [new ChatItem('No sessions found', '', '')];
            }

            // Get all JSON files
            const files = fs.readdirSync(sessionsDir)
                .filter((f: string) => f.endsWith('.json'))
                .map((f: string) => {
                    const filePath = path.join(sessionsDir, f);
                    const stats = fs.statSync(filePath);
                    return {
                        filename: f,
                        sessionId: f.replace('.json', ''),
                        mtime: stats.mtime,
                        size: (stats.size / 1024).toFixed(1) + ' KB'
                    };
                })
                .sort((a: any, b: any) => b.mtime.getTime() - a.mtime.getTime())
                .slice(0, 10);

            // Create chat items
            return files.map((file: any) => {
                const timestamp = file.mtime.toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                return new ChatItem(timestamp, file.sessionId, file.size);
            });

        } catch (error: any) {
            console.error('Error reading sessions:', error);
            return [new ChatItem('Error loading chats', '', '')];
        }
    }
}

class MemoryItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly contextValue: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: vscode.Command
    ) {
        super(label, collapsibleState);
        this.contextValue = contextValue;
    }
}

class ChatItem extends vscode.TreeItem {
    constructor(
        public readonly timestamp: string,
        public readonly sessionId: string,
        public readonly size: string
    ) {
        super(timestamp, vscode.TreeItemCollapsibleState.None);
        this.description = size;
        this.tooltip = `Session: ${sessionId}`;
        this.contextValue = 'chatSession';
        this.command = {
            command: 'soraMemory.openConversation',
            title: 'Open Conversation',
            arguments: [sessionId]
        };
    }
}
