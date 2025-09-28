// class ChatApp {
//     constructor() {
//         this.socket = io();
//         this.currentConversationId = null;
//         this.setupEventListeners();
//         this.setupSocketListeners();
//     }

//     setupEventListeners() {
//         const messageInput = document.getElementById('messageInput');
//         const sendBtn = document.getElementById('sendBtn');
//         const newChatBtn = document.getElementById('newChatBtn');

//         // Send message on button click
//         sendBtn.addEventListener('click', () => this.sendMessage());

//         // Send message on Enter key
//         messageInput.addEventListener('keypress', (e) => {
//             if (e.key === 'Enter') {
//                 this.sendMessage();
//             }
//         });

//         // New chat button
//         newChatBtn.addEventListener('click', () => {
//             this.socket.emit('new_conversation');
//         });

//         // Auto-focus input
//         messageInput.focus();
//     }

//     setupSocketListeners() {
//         this.socket.on('connect', () => {
//             console.log('Connected to server');
//         });

//         this.socket.on('conversation_started', (data) => {
//             this.currentConversationId = data.conversation_id;
//             if (data.welcome_message) {
//                 this.addMessage('assistant', data.welcome_message);
//             }
//         });

//         this.socket.on('message_response', (data) => {
//             this.addMessage('assistant', data.response);
//             this.updateUIAfterResponse(data);
//         });

//         this.socket.on('typing_start', () => {
//             this.showTypingIndicator();
//         });

//         this.socket.on('typing_stop', () => {
//             this.hideTypingIndicator();
//         });

//         this.socket.on('error', (data) => {
//             this.addMessage('assistant', `Error: ${data.message}`);
//             this.hideTypingIndicator();
//         });
//     }

//     sendMessage() {
//         const messageInput = document.getElementById('messageInput');
//         const message = messageInput.value.trim();

//         if (!message) return;

//         // Add user message to chat
//         this.addMessage('user', message);

//         // Clear input
//         messageInput.value = '';

//         // Disable input while processing
//         this.setInputState(false);

//         // Send message to server
//         this.socket.emit('send_message', {
//             message: message,
//             conversation_id: this.currentConversationId
//         });
//     }

//     addMessage(role, content) {
//         const chatMessages = document.getElementById('chatMessages');
//         const messageDiv = document.createElement('div');
//         messageDiv.className = `message ${role}-message`;

//         const contentDiv = document.createElement('div');
//         contentDiv.className = 'message-content';
        
//         // Use marked to parse Markdown for assistant messages
//         if (role === 'assistant') {
//             contentDiv.innerHTML = marked.parse(content);
//         } else {
//             contentDiv.textContent = content;
//         }

//         const timeDiv = document.createElement('div');
//         timeDiv.className = 'message-time';
//         timeDiv.textContent = new Date().toLocaleTimeString();

//         messageDiv.appendChild(contentDiv);
//         messageDiv.appendChild(timeDiv);
//         chatMessages.appendChild(messageDiv);

//         // Scroll to bottom
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//     }

//     showTypingIndicator() {
//         const typingIndicator = document.getElementById('typingIndicator');
//         typingIndicator.style.display = 'flex';
        
//         const chatMessages = document.getElementById('chatMessages');
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//     }

//     hideTypingIndicator() {
//         const typingIndicator = document.getElementById('typingIndicator');
//         typingIndicator.style.display = 'none';
//     }

//     setInputState(enabled) {
//         const messageInput = document.getElementById('messageInput');
//         const sendBtn = document.getElementById('sendBtn');

//         messageInput.disabled = !enabled;
//         sendBtn.disabled = !enabled;

//         if (enabled) {
//             messageInput.focus();
//         }
//     }

//     updateUIAfterResponse(data) {
//         this.setInputState(true);
        
//         // Add visual indicator for web navigation results
//         if (data.type === 'web_navigation') {
//             const lastMessage = document.querySelector('.assistant-message:last-child');
//             if (lastMessage) {
//                 const badge = document.createElement('span');
//                 badge.className = data.success ? 'success-badge' : 'error-badge';
//                 badge.textContent = data.success ? '✓ Web Search' : '✗ Search Failed';
//                 lastMessage.querySelector('.message-content').appendChild(badge);
//             }
//         }
//     }
// }

// // Initialize the chat app when page loads
// document.addEventListener('DOMContentLoaded', () => {
//     new ChatApp();
// });

class ChatApp {
    constructor() {
        this.socket = io();
        this.currentConversationId = null;
        this.downloadedFiles = [];
        this.setupEventListeners();
        this.setupSocketListeners();
        this.loadDownloadHistory();
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const newChatBtn = document.getElementById('newChatBtn');
        const downloadsBtn = document.getElementById('downloadsBtn');
        const modal = document.getElementById('downloadsModal');
        const closeModal = document.querySelector('.close-modal');

        // Send message on button click
        sendBtn.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // New chat button
        newChatBtn.addEventListener('click', () => {
            this.socket.emit('new_conversation');
        });

        // Downloads button
        downloadsBtn.addEventListener('click', () => {
            this.openDownloadsModal();
        });

        // Close modal
        closeModal.addEventListener('click', () => {
            this.closeDownloadsModal();
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeDownloadsModal();
            }
        });

        // Auto-focus input
        messageInput.focus();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('conversation_started', (data) => {
            this.currentConversationId = data.conversation_id;
            if (data.welcome_message) {
                this.addMessage('assistant', data.welcome_message);
            }
        });

        this.socket.on('message_response', (data) => {
            this.addMessage('assistant', data.response, data);
            this.updateUIAfterResponse(data);
        });

        this.socket.on('file_ready', (data) => {
            this.showDownloadToast(data);
            this.addToDownloadsHistory(data);
        });

        this.socket.on('files_list', (files) => {
            this.downloadedFiles = files;
            this.updateDownloadsModal();
        });

        this.socket.on('typing_start', () => {
            this.showTypingIndicator();
        });

        this.socket.on('typing_stop', () => {
            this.hideTypingIndicator();
        });

        this.socket.on('error', (data) => {
            this.addMessage('assistant', `Error: ${data.message}`);
            this.hideTypingIndicator();
        });
    }

    sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        messageInput.value = '';

        // Disable input while processing
        this.setInputState(false);

        // Send message to server
        this.socket.emit('send_message', {
            message: message,
            conversation_id: this.currentConversationId
        });
    }

    addMessage(role, content, responseData = {}) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Use marked to parse Markdown for assistant messages
        if (role === 'assistant') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);

        // Add file download section if file was created
        if (responseData.file_created && responseData.file_path) {
            const fileDownloadDiv = this.createFileDownloadSection(responseData);
            messageDiv.appendChild(fileDownloadDiv);
        }

        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    createFileDownloadSection(responseData) {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-download';

        const fileIcon = document.createElement('div');
        fileIcon.className = 'file-icon';
        fileIcon.textContent = this.getFileIcon(responseData.output_format);

        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';

        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = responseData.file_name;

        const fileSize = document.createElement('div');
        fileSize.className = 'file-size';
        fileSize.textContent = this.getFileTypeText(responseData.output_format);

        fileInfo.appendChild(fileName);
        fileInfo.appendChild(fileSize);

        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'download-btn';
        downloadBtn.textContent = 'Download';
        downloadBtn.addEventListener('click', () => {
            this.downloadFile(responseData.file_path, responseData.file_name);
        });

        fileDiv.appendChild(fileIcon);
        fileDiv.appendChild(fileInfo);
        fileDiv.appendChild(downloadBtn);

        return fileDiv;
    }

    getFileIcon(format) {
        const icons = {
            'json': '📊',
            'csv': '📈',
            'txt': '📄',
            'pdf': '📑',
            'text': '📝'
        };
        return icons[format] || '📁';
    }

    getFileTypeText(format) {
        const types = {
            'json': 'JSON Data File',
            'csv': 'CSV Spreadsheet',
            'txt': 'Text Document',
            'pdf': 'PDF Document',
            'text': 'Text Results'
        };
        return types[format] || 'Data File';
    }

    downloadFile(filePath, fileName) {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = `/download?file=${encodeURIComponent(filePath)}`;
        link.download = fileName;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    addToDownloadsHistory(fileData) {
        const downloadItem = {
            name: fileData.name,
            path: fileData.path,
            format: fileData.format,
            timestamp: new Date().toLocaleString()
        };

        this.downloadedFiles.unshift(downloadItem);
        
        // Keep only last 20 downloads
        if (this.downloadedFiles.length > 20) {
            this.downloadedFiles = this.downloadedFiles.slice(0, 20);
        }

        this.saveDownloadHistory();
        this.updateDownloadsModal();
    }

    loadDownloadHistory() {
        const saved = localStorage.getItem('webNavigatorDownloads');
        if (saved) {
            this.downloadedFiles = JSON.parse(saved);
        }
        this.updateDownloadsModal();
    }

    saveDownloadHistory() {
        localStorage.setItem('webNavigatorDownloads', JSON.stringify(this.downloadedFiles));
    }

    openDownloadsModal() {
        const modal = document.getElementById('downloadsModal');
        modal.style.display = 'block';
        this.updateDownloadsModal();
    }

    closeDownloadsModal() {
        const modal = document.getElementById('downloadsModal');
        modal.style.display = 'none';
    }

    updateDownloadsModal() {
        const downloadsList = document.getElementById('downloadsList');
        const noDownloads = document.getElementById('noDownloads');

        if (this.downloadedFiles.length === 0) {
            downloadsList.style.display = 'none';
            noDownloads.style.display = 'block';
            return;
        }

        downloadsList.style.display = 'block';
        noDownloads.style.display = 'none';
        downloadsList.innerHTML = '';

        this.downloadedFiles.forEach(file => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'download-item';

            const iconDiv = document.createElement('div');
            iconDiv.className = 'download-item-icon';
            iconDiv.textContent = this.getFileIcon(file.format);

            const infoDiv = document.createElement('div');
            infoDiv.className = 'download-item-info';

            const nameDiv = document.createElement('div');
            nameDiv.className = 'download-item-name';
            nameDiv.textContent = file.name;

            const dateDiv = document.createElement('div');
            dateDiv.className = 'download-item-date';
            dateDiv.textContent = file.timestamp;

            infoDiv.appendChild(nameDiv);
            infoDiv.appendChild(dateDiv);

            const actionBtn = document.createElement('button');
            actionBtn.className = 'download-item-action';
            actionBtn.textContent = 'Download';
            actionBtn.addEventListener('click', () => {
                this.downloadFile(file.path, file.name);
            });

            itemDiv.appendChild(iconDiv);
            itemDiv.appendChild(infoDiv);
            itemDiv.appendChild(actionBtn);
            downloadsList.appendChild(itemDiv);
        });
    }

    showDownloadToast(fileData) {
        const toast = document.getElementById('downloadToast');
        const toastMessage = toast.querySelector('.toast-message');
        const toastAction = toast.querySelector('.toast-action');

        toastMessage.textContent = `${fileData.name} is ready!`;
        toastAction.onclick = () => this.downloadFile(fileData.path, fileData.name);

        toast.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            toast.style.display = 'none';
        }, 5000);
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'flex';
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'none';
    }

    setInputState(enabled) {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.disabled = !enabled;
        sendBtn.disabled = !enabled;

        if (enabled) {
            messageInput.focus();
        }
    }

    updateUIAfterResponse(data) {
        this.setInputState(true);
        
        // Add visual indicator for web navigation results
        if (data.type === 'web_navigation') {
            const lastMessage = document.querySelector('.assistant-message:last-child');
            if (lastMessage) {
                const badge = document.createElement('span');
                badge.className = data.success ? 'success-badge' : 'error-badge';
                badge.textContent = data.success ? '✓ Web Search' : '✗ Search Failed';
                lastMessage.querySelector('.message-content').appendChild(badge);

                // Add format badge if file was created
                if (data.file_created) {
                    const formatBadge = document.createElement('span');
                    formatBadge.className = 'format-badge';
                    formatBadge.textContent = data.output_format.toUpperCase();
                    lastMessage.querySelector('.message-content').appendChild(formatBadge);
                }
            }
        }
    }
}

// Initialize the chat app when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});