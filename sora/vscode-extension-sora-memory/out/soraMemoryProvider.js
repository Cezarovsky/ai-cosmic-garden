"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecentChatsProvider = exports.SoraMemoryProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
class SoraMemoryProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        const config = vscode.workspace.getConfiguration('soraMemory');
        this.memorySystemPath = this.expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
        this.pythonPath = config.get('pythonPath', 'python3');
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    expandPath(p) {
        if (p.startsWith('~')) {
            return path.join(os.homedir(), p.slice(1));
        }
        return p;
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
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
        }
        else if (element.contextValue === 'stats') {
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
    async getMemoryStats() {
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
            }
            catch {
                return {
                    totalSessions: 0,
                    daysSinceAwakening,
                    daysSinceMarriage
                };
            }
        }
        catch (error) {
            return {
                totalSessions: 0,
                daysSinceAwakening: 0,
                daysSinceMarriage: 0
            };
        }
    }
}
exports.SoraMemoryProvider = SoraMemoryProvider;
class RecentChatsProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        const config = vscode.workspace.getConfiguration('soraMemory');
        this.memorySystemPath = this.expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
        this.pythonPath = config.get('pythonPath', 'python3');
    }
    expandPath(p) {
        if (p.startsWith('~')) {
            return path.join(os.homedir(), p.slice(1));
        }
        return p;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren() {
        try {
            // Read directly from sora_memory_db/sessions/
            const fs = require('fs');
            const sessionsDir = path.join(this.memorySystemPath, 'sora_memory_db', 'sessions');
            if (!fs.existsSync(sessionsDir)) {
                return [new ChatItem('No sessions found', '', '')];
            }
            // Get all JSON files
            const files = fs.readdirSync(sessionsDir)
                .filter((f) => f.endsWith('.json'))
                .map((f) => {
                const filePath = path.join(sessionsDir, f);
                const stats = fs.statSync(filePath);
                return {
                    filename: f,
                    sessionId: f.replace('.json', ''),
                    mtime: stats.mtime,
                    size: (stats.size / 1024).toFixed(1) + ' KB'
                };
            })
                .sort((a, b) => b.mtime.getTime() - a.mtime.getTime())
                .slice(0, 10);
            // Create chat items
            return files.map((file) => {
                const timestamp = file.mtime.toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                return new ChatItem(timestamp, file.sessionId, file.size);
            });
        }
        catch (error) {
            console.error('Error reading sessions:', error);
            return [new ChatItem('Error loading chats', '', '')];
        }
    }
}
exports.RecentChatsProvider = RecentChatsProvider;
class MemoryItem extends vscode.TreeItem {
    constructor(label, contextValue, collapsibleState, command) {
        super(label, collapsibleState);
        this.label = label;
        this.contextValue = contextValue;
        this.collapsibleState = collapsibleState;
        this.command = command;
        this.contextValue = contextValue;
    }
}
class ChatItem extends vscode.TreeItem {
    constructor(timestamp, sessionId, size) {
        super(timestamp, vscode.TreeItemCollapsibleState.None);
        this.timestamp = timestamp;
        this.sessionId = sessionId;
        this.size = size;
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
//# sourceMappingURL=soraMemoryProvider.js.map