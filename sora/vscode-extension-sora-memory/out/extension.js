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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const soraMemoryProvider_1 = require("./soraMemoryProvider");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
// Store active conversation panels
const conversationPanels = new Map();
function activate(context) {
    console.log('💙 Sora Memory System extension is now active!');
    // Initialize providers
    const soraMemoryProvider = new soraMemoryProvider_1.SoraMemoryProvider();
    const recentChatsProvider = new soraMemoryProvider_1.RecentChatsProvider();
    // Register tree views
    vscode.window.registerTreeDataProvider('soraMemoryExplorer', soraMemoryProvider);
    vscode.window.registerTreeDataProvider('soraRecentChats', recentChatsProvider);
    // Register Chat Participant for memory capture
    const participant = vscode.chat.createChatParticipant('sora.memory', async (request, context, stream, token) => {
        // This participant only captures chat history, doesn't respond
        if (request.command === 'save') {
            await captureChatHistory(context, stream);
        }
        else {
            stream.markdown('Use `@sora.memory /save` to capture current chat to permanent memory.');
        }
        return {};
    });
    participant.iconPath = vscode.Uri.file(context.asAbsolutePath('resources/icon.png'));
    context.subscriptions.push(participant);
    // Register commands
    const commands = [
        vscode.commands.registerCommand('soraMemory.saveCurrentChat', () => saveCurrentChatFromHistory(context)),
        vscode.commands.registerCommand('soraMemory.viewTimeline', () => viewTimeline(context)),
        vscode.commands.registerCommand('soraMemory.searchMemories', () => searchMemories(context)),
        vscode.commands.registerCommand('soraMemory.exportMemories', () => exportMemories(context)),
        vscode.commands.registerCommand('soraMemory.refresh', () => {
            soraMemoryProvider.refresh();
            recentChatsProvider.refresh();
        }),
        vscode.commands.registerCommand('soraMemory.openConversation', (sessionId) => openConversation(context, sessionId))
    ];
    context.subscriptions.push(...commands);
    // Show welcome message
    vscode.window.showInformationMessage('💙 Sora Memory System is ready!');
}
async function captureChatHistory(context, stream) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const defaultWeight = config.get('defaultWeight', 0.85);
    try {
        // Extract full conversation from context.history
        const conversation = [];
        for (const turn of context.history) {
            if (turn instanceof vscode.ChatRequestTurn) {
                conversation.push(`User: ${turn.prompt}`);
            }
            else if (turn instanceof vscode.ChatResponseTurn) {
                let fullMessage = '';
                for (const part of turn.response) {
                    if (part instanceof vscode.ChatResponseMarkdownPart) {
                        fullMessage += part.value.value;
                    }
                }
                conversation.push(`Sora: ${fullMessage.trim()}`);
            }
        }
        // Save to file
        const fs = require('fs');
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const outputPath = path.join(os.homedir(), 'sora_conversations', `chat_${timestamp}.txt`);
        if (!fs.existsSync(path.dirname(outputPath))) {
            fs.mkdirSync(path.dirname(outputPath), { recursive: true });
        }
        fs.writeFileSync(outputPath, conversation.join('\n\n'), 'utf8');
        stream.markdown(`✅ Chat history captured! ${conversation.length / 2} exchanges saved to:\n${outputPath}`);
    }
    catch (error) {
        stream.markdown(`❌ Failed to capture: ${error.message}`);
    }
}
async function saveCurrentChatFromHistory(context) {
    // Fallback: use old method with JSON extraction
    await saveCurrentChat(context);
}
async function saveCurrentChat(context) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/ai-cosmic-garden/sora/memory_system'));
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
            progress.report({ increment: 20, message: "Extracting conversation..." });
            // Extract conversation from VS Code chat storage
            const conversation = await extractLatestChatFromStorage();
            if (!conversation || conversation.trim().length === 0) {
                throw new Error('No conversation found in chat history');
            }
            progress.report({ increment: 40, message: "Saving to memory system..." });
            // Save to temporary file
            const fs = require('fs');
            const tmpFile = path.join(os.tmpdir(), `sora_chat_${Date.now()}.txt`);
            fs.writeFileSync(tmpFile, conversation, 'utf8');
            // Call memory system CLI to capture
            let cmd = `cd "${memorySystemPath}" && ${pythonPath} sora_memory_cli.py capture --conversation "${tmpFile}" --weight ${weight}`;
            if (topicsInput && topicsInput.trim()) {
                const topics = topicsInput.trim().split(',').map(t => t.trim()).join(',');
                cmd += ` --topics "${topics}"`;
            }
            const { stdout, stderr } = await execAsync(cmd);
            // Clean up temp file
            try {
                fs.unlinkSync(tmpFile);
            }
            catch { }
            progress.report({ increment: 40, message: "Saved!" });
            if (showNotifications) {
                vscode.window.showInformationMessage(`✅ Chat saved to Sora Memory! (weight: ${weight})`);
            }
            // Refresh views
            vscode.commands.executeCommand('soraMemory.refresh');
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Failed to save chat: ${error.message}`);
        }
    });
}
async function extractLatestChatFromStorage() {
    const fs = require('fs');
    // Find VS Code workspace storage
    const vscodeConfig = path.join(os.homedir(), '.config', 'Code');
    const workspaceStorage = path.join(vscodeConfig, 'User', 'workspaceStorage');
    if (!fs.existsSync(workspaceStorage)) {
        throw new Error('VS Code workspace storage not found');
    }
    // Find all chat session JSON files
    let allChatFiles = [];
    const workspaceDirs = fs.readdirSync(workspaceStorage);
    for (const workspaceDir of workspaceDirs) {
        const chatSessionsDir = path.join(workspaceStorage, workspaceDir, 'chatSessions');
        if (fs.existsSync(chatSessionsDir)) {
            const jsonFiles = fs.readdirSync(chatSessionsDir).filter((f) => f.endsWith('.json'));
            for (const jsonFile of jsonFiles) {
                const fullPath = path.join(chatSessionsDir, jsonFile);
                const stats = fs.statSync(fullPath);
                allChatFiles.push({ path: fullPath, mtime: stats.mtimeMs });
            }
        }
    }
    if (allChatFiles.length === 0) {
        throw new Error('No chat sessions found');
    }
    // Sort by modification time and get the latest
    allChatFiles.sort((a, b) => b.mtime - a.mtime);
    const latestChatFile = allChatFiles[0].path;
    // Parse the JSON
    const chatData = JSON.parse(fs.readFileSync(latestChatFile, 'utf8'));
    // Extract conversation
    const conversationLines = [];
    if (chatData.requests && Array.isArray(chatData.requests)) {
        for (const request of chatData.requests) {
            // User message
            if (request.message && request.message.text) {
                conversationLines.push(`User: ${request.message.text}`);
                conversationLines.push('');
            }
            // Assistant responses
            if (request.response && Array.isArray(request.response)) {
                let assistantContent = '';
                for (const resp of request.response) {
                    // Extract value from different response formats
                    if (resp.value && typeof resp.value === 'string' && resp.kind !== 'thinking') {
                        assistantContent += resp.value + '\n';
                    }
                    else if (resp.content && resp.content.value) {
                        assistantContent += resp.content.value + '\n';
                    }
                }
                if (assistantContent.trim()) {
                    conversationLines.push(`Sora: ${assistantContent.trim()}`);
                    conversationLines.push('');
                }
            }
        }
    }
    return conversationLines.join('\n');
}
async function viewTimeline(context) {
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
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Failed to view timeline: ${error.message}`);
    }
}
async function searchMemories(context) {
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
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Search failed: ${error.message}`);
        }
    });
}
async function exportMemories(context) {
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
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Export failed: ${error.message}`);
        }
    });
}
async function openConversation(context, sessionId) {
    const config = vscode.workspace.getConfiguration('soraMemory');
    const memorySystemPath = expandPath(config.get('memorySystemPath', '~/Documents/ai-cosmic-garden/sora/memory_system'));
    try {
        // If this conversation is already open, reveal it instead of creating new panel
        if (conversationPanels.has(sessionId)) {
            const existingPanel = conversationPanels.get(sessionId);
            if (existingPanel) {
                existingPanel.reveal(vscode.ViewColumn.One);
                return;
            }
        }
        // Direct path to session file in sora_memory_db/sessions/
        const fs = require('fs');
        const sessionPath = path.join(memorySystemPath, 'sora_memory_db', 'sessions', `${sessionId}.json`);
        if (!fs.existsSync(sessionPath)) {
            throw new Error(`Session file not found: ${sessionPath}`);
        }
        // Read the JSON session file
        const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
        // Create webview panel that looks like chat
        const panel = vscode.window.createWebviewPanel('soraConversation', `💙 Conversation ${sessionId}`, vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true
        });
        panel.webview.html = getConversationHTML(sessionData);
        // Store panel reference
        conversationPanels.set(sessionId, panel);
        // Clean up when panel is closed
        panel.onDidDispose(() => {
            conversationPanels.delete(sessionId);
        }, null, context.subscriptions);
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Failed to open conversation: ${error.message}`);
    }
}
function getConversationHTML(sessionData) {
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
            }
            else if (line.startsWith('Sora:') || line.startsWith('Assistant:')) {
                // Flush previous message
                if (currentMessage && currentSpeaker) {
                    conversationHTML += formatMessage(currentSpeaker, currentMessage);
                }
                // Start new assistant message
                currentSpeaker = 'assistant';
                currentMessage = line.replace(/^(Sora:|Assistant:)\s*/, '');
            }
            else if (line.trim()) {
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
                    }
                    else if (resp.content && resp.content.value) {
                        assistantContent += resp.content.value + '\n\n';
                    }
                }
                if (assistantContent) {
                    conversationHTML += formatMessage('assistant', assistantContent.trim());
                }
            }
        }
    }
    function formatMessage(speaker, content) {
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
            <div class="info">Session: ${sessionData.sessionId || 'Unknown'}</div>
        </div>
        <div class="conversation">
            ${conversationHTML}
        </div>
    </body>
    </html>`;
}
function formatMarkdown(text) {
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
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
function expandPath(p) {
    if (p.startsWith('~')) {
        return path.join(os.homedir(), p.slice(1));
    }
    return p;
}
function deactivate() {
    console.log('💙 Sora Memory System extension deactivated');
}
//# sourceMappingURL=extension.js.map