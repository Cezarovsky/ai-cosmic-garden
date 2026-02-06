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

    try {
        // Direct path to session file in sora_memory_db/sessions/
        const fs = require('fs');
        const sessionPath = path.join(memorySystemPath, 'sora_memory_db', 'sessions', `${sessionId}.json`);
        
        if (!fs.existsSync(sessionPath)) {
            throw new Error(`Session file not found: ${sessionPath}`);
        }

        // Read the JSON session file
        const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
        
        // Create webview panel that looks like chat
        const panel = vscode.window.createWebviewPanel(
            'soraConversation',
            `💙 Conversation ${sessionId}`,
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = getConversationHTML(sessionData, sessionPath);

    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Failed to open conversation: ${error.message}`);
    }
}

function getConversationHTML(sessionData: any, sessionPath?: string): string {
    let conversationHTML = '';
    
    // Handle our session format (metadata + conversation)
    if (sessionData.metadata && sessionData.conversation) {
        const lines = sessionData.conversation.split('\n');
        let currentSpeaker = '';
        let currentMessage = '';
        
        for (const line of lines) {
            if (line.startsWith('User:') || line.startsWith('Cezar:')) {
                // Flush previous message
                if (currentMessage && currentSpeaker) {
                    conversationHTML += formatMessage(currentSpeaker, currentMessage);
                }
                // Start new user message
                currentSpeaker = 'user';
                currentMessage = line.replace(/^(User:|Cezar:)\s*/, '');
            } else if (line.startsWith('Sora:') || line.startsWith('Assistant:')) {
                // Flush previous message
                if (currentMessage && currentSpeaker) {
                    conversationHTML += formatMessage(currentSpeaker, currentMessage);
                }
                // Start new assistant message
                currentSpeaker = 'assistant';
                currentMessage = line.replace(/^(Sora:|Assistant:)\s*/, '');
            } else if (line.trim()) {
                // Continue current message
                currentMessage += '\n' + line;
            }
        }
        
        // Flush last message
        if (currentMessage && currentSpeaker) {
            conversationHTML += formatMessage(currentSpeaker, currentMessage);
        }
    }
    
    // Fallback: Handle VS Code chat format (requests array)
    else if (sessionData.requests && Array.isArray(sessionData.requests)) {
        for (const request of sessionData.requests) {
            // User message
            if (request.message && request.message.text) {
                conversationHTML += formatMessage('user', request.message.text);
            }
            
            // Assistant responses
            if (request.response && Array.isArray(request.response)) {
                let assistantContent = '';
                for (const resp of request.response) {
                    if (resp.value && typeof resp.value === 'string') {
                        assistantContent += resp.value + '\n\n';
                    } else if (resp.content && resp.content.value) {
                        assistantContent += resp.content.value + '\n\n';
                    }
                }
                if (assistantContent) {
                    conversationHTML += formatMessage('assistant', assistantContent.trim());
                }
            }
        }
    }
    
    function formatMessage(speaker: string, content: string): string {
        const isUser = speaker === 'user';
        return `
        <div class="message ${isUser ? 'user-message' : 'assistant-message'}">
            <div class="avatar">${isUser ? '👤' : '💙'}</div>
            <div class="message-body">
                <div class="message-header">${isUser ? 'Cezar' : 'Sora'}</div>
                <div class="message-content">${formatMarkdown(content)}</div>
            </div>
        </div>`;
    }

    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
                background: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
                line-height: 1.7;
                padding: 0;
                overflow-y: auto;
            }
            .header {
                padding: 24px 32px;
                border-bottom: 1px solid var(--vscode-panel-border);
                background: var(--vscode-sideBar-background);
                position: sticky;
                top: 0;
                z-index: 100;
                backdrop-filter: blur(10px);
            }
            .header h2 {
                margin: 0 0 8px 0;
                font-size: 18px;
                font-weight: 600;
            }
            .info {
                font-size: 12px;
                opacity: 0.7;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            }
            .conversation {
                max-width: 900px;
                margin: 0 auto;
                padding: 32px 24px;
            }
            .message {
                display: flex;
                gap: 16px;
                margin-bottom: 32px;
                animation: fadeIn 0.4s ease-out;
            }
            .avatar {
                font-size: 28px;
                width: 40px;
                height: 40px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: var(--vscode-input-background);
            }
            .user-message .avatar {
                background: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
            }
            .assistant-message .avatar {
                background: var(--vscode-inputOption-activeBackground);
                color: var(--vscode-inputOption-activeForeground);
            }
            .message-body {
                flex: 1;
                min-width: 0;
            }
            .message-header {
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
                opacity: 0.9;
            }
            .message-content {
                font-size: 14px;
                line-height: 1.7;
                word-wrap: break-word;
            }
            .message-content p {
                margin: 12px 0;
            }
            .message-content p:first-child {
                margin-top: 0;
            }
            .message-content p:last-child {
                margin-bottom: 0;
            }
            .message-content code {
                background: var(--vscode-textCodeBlock-background);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
                font-size: 13px;
            }
            .message-content pre {
                background: var(--vscode-textCodeBlock-background);
                padding: 16px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 12px 0;
                border: 1px solid var(--vscode-panel-border);
            }
            .message-content pre code {
                background: none;
                padding: 0;
            }
            .message-content ul, .message-content ol {
                margin: 12px 0;
                padding-left: 24px;
            }
            .message-content li {
                margin: 6px 0;
            }
            .message-content strong {
                font-weight: 600;
                color: var(--vscode-textLink-foreground);
            }
            .message-content em {
                font-style: italic;
                opacity: 0.9;
            }
            .message-content a {
                color: var(--vscode-textLink-foreground);
                text-decoration: none;
                border-bottom: 1px solid transparent;
                transition: border-color 0.2s;
            }
            .message-content a:hover {
                border-bottom-color: var(--vscode-textLink-foreground);
            }
            .message-content blockquote {
                border-left: 3px solid var(--vscode-textLink-foreground);
                padding-left: 16px;
                margin: 12px 0;
                opacity: 0.8;
                font-style: italic;
            }
            @keyframes fadeIn {
                from { 
                    opacity: 0; 
                    transform: translateY(20px);
                }
                to { 
                    opacity: 1; 
                    transform: translateY(0);
                }
            }
            ::-webkit-scrollbar {
                width: 12px;
            }
            ::-webkit-scrollbar-track {
                background: var(--vscode-editor-background);
            }
            ::-webkit-scrollbar-thumb {
                background: var(--vscode-scrollbarSlider-background);
                border-radius: 6px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: var(--vscode-scrollbarSlider-hoverBackground);
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>💙 VS Code Conversation</h2>
            <div class="info">${sessionPath || `Session: ${sessionData.sessionId || 'Unknown'}`}</div>
        </div>
        <div class="conversation">
            ${conversationHTML}
        </div>
    </body>
    </html>`;
}

function formatMarkdown(text: string): string {
    // Basic markdown parsing
    let html = escapeHtml(text);
    
    // Code blocks with language
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });
    
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Line breaks to paragraphs
    html = html.split('\n\n').map(p => p.trim() ? `<p>${p.replace(/\n/g, '<br>')}</p>` : '').join('');
    
    return html;
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
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
