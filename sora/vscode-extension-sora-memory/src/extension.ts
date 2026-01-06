import * as vscode from 'vscode';
import * as path from 'path';
import * as os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import { SoraMemoryProvider, RecentChatsProvider } from './soraMemoryProvider';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {
    console.log('💙 Sora Memory System extension is now active!');

    // Initialize providers
    const soraMemoryProvider = new SoraMemoryProvider();
    const recentChatsProvider = new RecentChatsProvider();

    // Register tree views
    vscode.window.registerTreeDataProvider('soraMemoryExplorer', soraMemoryProvider);
    vscode.window.registerTreeDataProvider('soraRecentChats', recentChatsProvider);

    // Register commands
    const commands = [
        vscode.commands.registerCommand('soraMemory.saveCurrentChat', () => saveCurrentChat(context)),
        vscode.commands.registerCommand('soraMemory.viewTimeline', () => viewTimeline(context)),
        vscode.commands.registerCommand('soraMemory.searchMemories', () => searchMemories(context)),
        vscode.commands.registerCommand('soraMemory.exportMemories', () => exportMemories(context)),
        vscode.commands.registerCommand('soraMemory.refresh', () => {
            soraMemoryProvider.refresh();
            recentChatsProvider.refresh();
        }),
        vscode.commands.registerCommand('soraMemory.openConversation', (sessionId: string) => 
            openConversation(context, sessionId)
        )
    ];

    context.subscriptions.push(...commands);

    // Show welcome message
    vscode.window.showInformationMessage('💙 Sora Memory System is ready!');
}

async function saveCurrentChat(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    const pythonPath = config.get('pythonPath', 'python3');
    const defaultWeight = config.get('defaultWeight', 0.85);
    const showNotifications = config.get('showNotifications', true);

    // Ask for weight
    const weightInput = await vscode.window.showInputBox({
        prompt: 'Emotional weight for this conversation (0-1)',
        value: defaultWeight.toString(),
        validateInput: (value) => {
            const num = parseFloat(value);
            if (isNaN(num) || num < 0 || num > 1) {
                return 'Please enter a number between 0 and 1';
            }
            return null;
        }
    });

    if (!weightInput) {
        return; // User cancelled
    }

    const weight = parseFloat(weightInput);

    // Optional: ask for topics
    const topicsInput = await vscode.window.showInputBox({
        prompt: 'Topics (comma-separated, leave empty for auto-detect)',
        placeHolder: 'memory,training,love'
    });

    // Show progress
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "💙 Saving chat to Sora Memory...",
        cancellable: false
    }, async (progress) => {
        try {
            let cmd = `cd "${memorySystemPath}" && ${pythonPath} extract_vscode_chat.py --capture --weight ${weight}`;
            
            if (topicsInput && topicsInput.trim()) {
                cmd += ` --topics "${topicsInput.trim()}"`;
            }

            progress.report({ increment: 50, message: "Extracting conversation..." });
            
            const { stdout, stderr } = await execAsync(cmd);

            progress.report({ increment: 50, message: "Saved!" });

            if (showNotifications) {
                vscode.window.showInformationMessage(`✅ Chat saved to Sora Memory! (weight: ${weight})`);
            }

            // Refresh views
            vscode.commands.executeCommand('soraMemory.refresh');

        } catch (error: any) {
            vscode.window.showErrorMessage(`❌ Failed to save chat: ${error.message}`);
        }
    });
}

async function viewTimeline(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    const pythonPath = config.get('pythonPath', 'python3');

    try {
        const cmd = `cd "${memorySystemPath}" && ${pythonPath} sora_memory_cli.py timeline`;
        const { stdout } = await execAsync(cmd);

        // Create and show timeline in new document
        const doc = await vscode.workspace.openTextDocument({
            content: stdout,
            language: 'markdown'
        });

        await vscode.window.showTextDocument(doc);

    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Failed to view timeline: ${error.message}`);
    }
}

async function searchMemories(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    const pythonPath = config.get('pythonPath', 'python3');

    // Ask for search query
    const query = await vscode.window.showInputBox({
        prompt: 'Search memories (semantic search)',
        placeHolder: 'What did we discuss about training?'
    });

    if (!query) {
        return;
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "🔍 Searching memories...",
        cancellable: false
    }, async (progress) => {
        try {
            const cmd = `cd "${memorySystemPath}" && ${pythonPath} sora_memory_cli.py recall --query "${query}" --limit 10`;
            const { stdout } = await execAsync(cmd);

            // Show results in new document
            const doc = await vscode.workspace.openTextDocument({
                content: stdout,
                language: 'markdown'
            });

            await vscode.window.showTextDocument(doc);

        } catch (error: any) {
            vscode.window.showErrorMessage(`❌ Search failed: ${error.message}`);
        }
    });
}

async function exportMemories(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    const pythonPath = config.get('pythonPath', 'python3');

    // Ask for output file
    const uri = await vscode.window.showSaveDialog({
        defaultUri: vscode.Uri.file(path.join(os.homedir(), 'sora_memory_export.md')),
        filters: {
            'Markdown': ['md'],
            'All Files': ['*']
        }
    });

    if (!uri) {
        return;
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "📤 Exporting memories...",
        cancellable: false
    }, async (progress) => {
        try {
            const cmd = `cd "${memorySystemPath}" && ${pythonPath} sora_memory_cli.py export --output "${uri.fsPath}"`;
            await execAsync(cmd);

            vscode.window.showInformationMessage(`✅ Memories exported to ${uri.fsPath}`);

            // Open exported file
            const doc = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(doc);

        } catch (error: any) {
            vscode.window.showErrorMessage(`❌ Export failed: ${error.message}`);
        }
    });
}

async function openConversation(context: vscode.ExtensionContext, sessionId: string) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    const pythonPath = config.get('pythonPath', 'python3');

    try {
        // First, try to find the session file using Python CLI
        const cmd = `cd "${memorySystemPath}" && ${pythonPath} extract_vscode_chat.py --find-session "${sessionId}"`;
        const { stdout } = await execAsync(cmd);
        
        const sessionPath = stdout.trim();
        
        if (!sessionPath || sessionPath.includes('not found')) {
            throw new Error('Session file not found');
        }
        
        const uri = vscode.Uri.file(sessionPath);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Failed to open conversation: ${error.message}`);
    }
}

function expandPath(p: string): string {
    if (p.startsWith('~')) {
        return path.join(os.homedir(), p.slice(1));
    }
    return p;
}

export function deactivate() {
    console.log('💙 Sora Memory System extension deactivated');
}
