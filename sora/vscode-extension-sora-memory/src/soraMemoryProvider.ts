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
            // Get recent chats from Python CLI
            const cmd = `cd "${this.memorySystemPath}" && ${this.pythonPath} extract_vscode_chat.py --list --limit 10`;
            const { stdout } = await execAsync(cmd);

            // Parse output
            const sessions: ChatItem[] = [];
            const lines = stdout.split('\n');
            let currentSession: any = {};

            for (const line of lines) {
                if (line.includes('📅')) {
                    if (currentSession.timestamp) {
                        sessions.push(new ChatItem(
                            currentSession.timestamp,
                            currentSession.id,
                            currentSession.size
                        ));
                    }
                    currentSession = { timestamp: line.replace('📅 ', '').trim() };
                } else if (line.includes('ID:')) {
                    currentSession.id = line.split('ID:')[1].trim();
                } else if (line.includes('Size:')) {
                    currentSession.size = line.split('Size:')[1].trim();
                }
            }

            // Add last session
            if (currentSession.timestamp) {
                sessions.push(new ChatItem(
                    currentSession.timestamp,
                    currentSession.id,
                    currentSession.size
                ));
            }

            return sessions.slice(0, 10);
        } catch (error) {
            return [new ChatItem('No recent chats found', '', '')];
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
