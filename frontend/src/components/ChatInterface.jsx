import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import {
    Send, Plus, MessageSquare, LogOut, Settings, User,
    Paperclip, FileText, X, AlertTriangle, Check, Copy,
    StopCircle, Sidebar, Loader2, ChevronDown, Bot
} from 'lucide-react';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activeDocument, setActiveDocument] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [streamingContent, setStreamingContent] = useState(''); // For visual typing effect
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const textareaRef = useRef(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [input]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, streamingContent]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.pdf')) {
            alert('Please upload a PDF file.');
            return;
        }

        const formData = new FormData();
        formData.append('files', file);

        // Optimistic UI for upload
        const tempId = Date.now();
        setMessages(prev => [...prev, {
            id: tempId,
            role: 'system',
            content: `Uploading ${file.name}...`,
            type: 'loading'
        }]);

        try {
            await api.post('/ingest/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setActiveDocument(file.name);

            // Replace loading message with success
            setMessages(prev => prev.map(msg =>
                msg.id === tempId
                    ? { ...msg, content: `Document "${file.name}" ready for analysis.`, type: 'success' }
                    : msg
            ));
        } catch (error) {
            setMessages(prev => prev.map(msg =>
                msg.id === tempId
                    ? { ...msg, content: `Failed to upload ${file.name}.`, type: 'error' }
                    : msg
            ));
        } finally {
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userText = input;
        setInput('');
        if (textareaRef.current) textareaRef.current.style.height = 'auto';

        const userMessage = { role: 'user', content: userText };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        // Add thinking indicator
        const thinkingId = Date.now();
        setMessages(prev => [...prev, {
            id: thinkingId,
            role: 'assistant',
            content: 'Analyzing your query...',
            isThinking: true
        }]);

        try {
            const payload = { query: userText };
            if (sessionId) payload.session_id = sessionId;

            const response = await api.post('/query/', payload);
            const data = response.data.data;

            if (!sessionId) setSessionId(response.data.session_id);

            // Remove thinking indicator and add actual response
            setMessages(prev => prev.filter(msg => msg.id !== thinkingId));

            // Use the new conversational response field
            const botMessage = {
                role: 'assistant',
                content: data.response,  // Primary conversational response
                status: data.status,
                reasoning: data.reasoning,
                sources: data.sources,
                relevant_clauses: data.relevant_clauses,
                conversation_type: data.conversation_type
            };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            // Remove thinking indicator
            setMessages(prev => prev.filter(msg => msg.id !== thinkingId));

            setMessages(prev => [...prev, {
                role: 'system',
                content: "Error generating response. Please check your connection.",
                type: 'error'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewChat = () => {
        setMessages([]);
        setSessionId(null);
        setActiveDocument(null);
    };

    const MessageRow = ({ msg }) => {
        const isUser = msg.role === 'user';
        const isSystem = msg.role === 'system';
        const isThinking = msg.isThinking;
        const [showDetails, setShowDetails] = React.useState(false);

        if (isSystem) {
            return (
                <div className="w-full text-center py-5 border-b border-black/10 dark:border-gray-900/50 text-gray-500 text-sm">
                    {msg.type === 'loading' && <Loader2 className="w-4 h-4 animate-spin inline mr-2" />}
                    {msg.type === 'error' && <AlertTriangle className="w-4 h-4 text-red-400 inline mr-2" />}
                    {msg.type === 'success' && <Check className="w-4 h-4 text-green-400 inline mr-2" />}
                    {msg.content}
                </div>
            );
        }

        return (
            <div className={`group w-full text-gray-800 dark:text-gray-100 border-b border-black/10 dark:border-gray-900/50 ${isUser ? 'dark:bg-[#343541]' : 'bg-gray-50 dark:bg-[#444654]'}`}>
                <div className="text-base gap-4 md:gap-6 md:max-w-2xl lg:max-w-xl xl:max-w-3xl p-4 md:py-6 flex lg:px-0 m-auto">
                    {/* Avatar */}
                    <div className="flex-shrink-0 flex flex-col relative items-end">
                        <div className={`w-[30px] h-[30px] rounded-sm flex items-center justify-center ${isUser ? 'bg-[#5436DA]' : 'bg-[#19c37d]'}`}>
                            {isUser ? (
                                <User className="w-5 h-5 text-white" />
                            ) : (
                                <svg width="41" height="41" viewBox="0 0 41 41" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-white" strokeWidth="2.5" stroke="currentColor">
                                    <path d="M37.5324 16.8707C37.9808 15.5241 38.1363 14.0974 37.9886 12.6859C37.8409 11.2744 37.3938 9.91076 36.676 8.68715C35.9582 7.46354 34.9867 6.40775 33.8268 5.59098C32.6669 4.77421 31.3459 4.21464 29.9519 3.94994C28.558 3.68524 27.123 3.72149 25.7436 4.05629C24.3642 4.39108 23.072 4.01758 21.9542 5.89243C20.8364 6.76728 19.9176 7.85962 19.2605 9.1C18.4239 9.17643 17.5878 9.17643 16.7512 9.1C16.92 8.76634 17.1082 8.44199 17.3155 8.12788C17.5227 7.81377 17.7495 7.51052 17.9953 7.21896C18.2411 6.92741 18.5052 6.64836 18.7849 6.38131C19.0645 6.11425 19.3582 5.85984 19.6631 5.61803C19.9679 5.37622 20.2829 5.14728 20.6074 4.93175L20.6277 5.06013L37.5324 16.8707Z" fill="currentColor" />
                                </svg>
                            )}
                        </div>
                    </div>

                    {/* Content */}
                    <div className="relative flex-1 overflow-hidden">
                        {/* Thinking Indicator */}
                        {isThinking ? (
                            <div className="flex items-center gap-2 text-gray-400">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="animate-pulse">{msg.content}</span>
                            </div>
                        ) : (
                            <>
                                {/* Main conversational response - Concise and direct */}
                                <div className="prose prose-invert min-w-full whitespace-pre-wrap leading-7 text-gray-100">
                                    {msg.content}
                                </div>

                                {/* Status Badge - Show immediately after response for compliance queries */}
                                {!isUser && msg.status && (
                                    <div className="mt-3 flex items-center gap-2">
                                        <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full ${msg.status === 'Compliant'
                                            ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                                            msg.status === 'Non-Compliant'
                                                ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                                                'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                                            }`}>
                                            {msg.status === 'Compliant' && <Check className="w-3 h-3" />}
                                            {msg.status === 'Non-Compliant' && <AlertTriangle className="w-3 h-3" />}
                                            {msg.status === 'Needs Review' && <AlertTriangle className="w-3 h-3" />}
                                            {msg.status.toUpperCase()}
                                        </span>
                                    </div>
                                )}

                                {/* Detailed Analysis Button - More prominent */}
                                {!isUser && msg.reasoning && (
                                    <div className="mt-4">
                                        <button
                                            onClick={() => setShowDetails(!showDetails)}
                                            className="group/btn inline-flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200"
                                        >
                                            <FileText className="w-4 h-4" />
                                            <span className="font-medium">
                                                {showDetails ? 'Hide detailed analysis' : 'Show detailed analysis'}
                                            </span>
                                            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showDetails ? 'rotate-180' : ''}`} />
                                        </button>

                                        {/* Detailed Analysis Panel */}
                                        {showDetails && (
                                            <div className="mt-3 p-4 bg-gradient-to-br from-black/30 to-black/20 rounded-lg border border-white/10 shadow-lg">
                                                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/10">
                                                    <FileText className="w-4 h-4 text-blue-400" />
                                                    <h4 className="font-semibold text-sm text-gray-200">Comprehensive Technical Analysis</h4>
                                                </div>
                                                <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                                                    {msg.reasoning}
                                                </div>

                                                {/* Relevant Clauses if available */}
                                                {msg.relevant_clauses && msg.relevant_clauses.length > 0 && (
                                                    <div className="mt-4 pt-3 border-t border-white/10">
                                                        <div className="text-xs font-medium text-gray-400 mb-2">Relevant Regulatory Clauses:</div>
                                                        <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
                                                            {msg.relevant_clauses.map((clause, i) => (
                                                                <li key={i}>{clause}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Source Citations */}
                                {!isUser && msg.sources && msg.sources.length > 0 && (
                                    <div className="mt-4 pt-3 border-t border-white/10">
                                        <div className="text-xs font-medium text-gray-400 mb-2">Sources Referenced:</div>
                                        <div className="flex flex-wrap gap-2">
                                            {msg.sources.map((src, i) => (
                                                <div
                                                    key={i}
                                                    className="group/src relative flex items-center gap-1.5 bg-black/30 hover:bg-black/50 px-3 py-1.5 rounded-md text-xs text-gray-400 hover:text-gray-300 cursor-pointer transition-all border border-white/5 hover:border-white/10"
                                                    title={src.excerpt}
                                                >
                                                    <FileText className="w-3 h-3 text-blue-400" />
                                                    <span className="max-w-[150px] truncate font-medium">{src.document_name}</span>
                                                    {src.page_number && <span className="opacity-50">• p{src.page_number}</span>}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>


                    {/* Hover Actions */}
                    <div className="text-gray-400 flex self-start lg:self-center justify-center mt-2 lg:mt-0 lg:ml-2 gap-2 md:gap-3 lg:absolute lg:top-0 lg:translate-x-full lg:right-0 lg:mt-0 lg:pl-2 visible lg:invisible lg:group-hover:visible">
                        <button className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition" onClick={() => navigator.clipboard.writeText(msg.content)}>
                            <Copy className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="flex h-screen overflow-hidden bg-[#343541]">
            {/* Sidebar */}
            <div className={`${isSidebarOpen ? 'w-[260px]' : 'w-0'} bg-[#202123] flex-shrink-0 transition-all duration-300 ease-in-out overflow-hidden flex flex-col border-r border-white/10 relative`}>
                <div className="p-2 gap-2 flex flex-col h-full">
                    {/* New Chat Button */}
                    <button
                        onClick={handleNewChat}
                        className="flex px-3 py-3 items-center gap-3 rounded-md border border-white/20 hover:bg-[#2A2B32] text-white text-sm transition-colors text-left"
                    >
                        <Plus className="w-4 h-4" />
                        New chat
                    </button>

                    {/* History Section (Mock) */}
                    <div className="flex-1 overflow-y-auto overflow-x-hidden my-2">
                        <div className="flex flex-col gap-2 pb-2 text-gray-100 text-sm">
                            <span className="px-3 text-xs font-medium text-gray-500 py-2">Today</span>
                            {activeDocument ? (
                                <button className="flex px-3 py-3 items-center gap-3 relative rounded-md bg-[#343541]/50 hover:bg-[#2A2B32] break-all group pr-2">
                                    <MessageSquare className="w-4 h-4" />
                                    <div className="flex-1 text-ellipsis max-h-5 overflow-hidden break-all relative">
                                        Analysis: {activeDocument}
                                        <div className="absolute inset-y-0 right-0 w-8 z-10 bg-gradient-to-l from-[#202123] group-hover:from-[#2A2B32]" />
                                    </div>
                                </button>
                            ) : (
                                <div className="px-3 text-gray-500 italic text-xs">No active sessions</div>
                            )}
                        </div>
                    </div>

                    {/* User Profile / Settings */}
                    <div className="border-t border-white/20 pt-2">
                        <button className="flex px-3 py-3 items-center gap-3 rounded-md hover:bg-[#2A2B32] text-white text-sm transition-colors w-full text-left">
                            <User className="w-4 h-4" />
                            <div className="flex-1 font-medium">Compliance Officer</div>
                            <Settings className="w-4 h-4 text-gray-400" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex flex-col flex-1 relative h-full max-w-full">
                {/* Header (Mobile / Active Doc) */}
                <div className="sticky top-0 z-10 flex items-center p-2 text-gray-500 bg-[#343541] border-b border-black/5 md:hidden">
                    <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="-ml-0.5 -mt-0.5 inline-flex h-10 w-10 items-center justify-center rounded-md hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white dark:hover:text-white">
                        <Sidebar className="w-6 h-6" />
                    </button>
                    <div className="mx-auto font-semibold">
                        {activeDocument || 'New Chat'}
                    </div>
                </div>

                {/* Model Selector Bar (Visual Only - like GPT-4 selector) */}
                <div className="hidden md:flex w-full items-center justify-center gap-1 p-4 border-b border-black/5 dark:border-white/5 bg-[#343541] text-gray-200 font-medium text-sm">
                    <span>Compliance Model 3.5</span>
                    <ChevronDown className="w-3 h-3 text-gray-400 opacity-50" />
                </div>

                {/* Messages Stream */}
                <div className="flex-1 overflow-y-auto scrollbar-trigger w-full">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-white px-2">
                            <div className="bg-white/10 p-4 rounded-full mb-6">
                                <Bot className="w-8 h-8" />
                            </div>
                            <h2 className="text-2xl font-semibold mb-8">ComplianceGPT</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
                                <div className="flex flex-col gap-3.5 w-full">
                                    <div className="flex flex-col gap-2 w-full text-center">
                                        <h3 className="text-lg font-normal mb-2"><br />Capabilities</h3>
                                        <button className="w-full bg-white/5 p-3 rounded-md hover:bg-black/20 text-sm">"Analyze uploaded PDF for risks"</button>
                                        <button className="w-full bg-white/5 p-3 rounded-md hover:bg-black/20 text-sm">"What are the audit requirements?"</button>
                                        <button className="w-full bg-white/5 p-3 rounded-md hover:bg-black/20 text-sm">"Check for GDPR compliance"</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col pb-32">
                            {messages.map((msg, idx) => (
                                <MessageRow key={idx} msg={msg} />
                            ))}
                        </div>
                    )}
                </div>

                {/* Input Area (Floating at bottom) */}
                <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#343541] via-[#343541] to-transparent pt-10 pb-6 px-4">
                    <div className="max-w-3xl mx-auto">
                        {/* Input Box */}
                        <div className="relative flex items-end w-full p-3 bg-[#40414F] rounded-xl border border-black/10 dark:border-gray-900/50 shadow-xs overflow-hidden ring-offset-2 focus-within:ring-2 ring-blue-500/50">
                            {/* Upload Button */}
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="p-2 mr-2 text-gray-400 hover:text-white transition-colors"
                                title="Upload PDF"
                            >
                                <Paperclip className="w-5 h-5" />
                            </button>
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileUpload}
                                className="hidden"
                                accept=".pdf"
                            />

                            <textarea
                                ref={textareaRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSend();
                                    }
                                }}
                                placeholder="Send a message..."
                                rows={1}
                                className="w-full max-h-[200px] py-2 bg-transparent border-none text-white focus:ring-0 focus:outline-none resize-none m-0 text-base scrollbar-hide"
                                style={{ maxHeight: '200px' }}
                            />

                            <button
                                onClick={handleSend}
                                disabled={isLoading || !input.trim()}
                                className={`p-2 ml-2 rounded-md transition-colors ${input.trim()
                                    ? 'bg-[#19c37d] text-white hover:bg-[#15a468]'
                                    : 'bg-transparent text-gray-500 cursor-not-allowed'
                                    }`}
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="text-center mt-2 text-xs text-gray-400/70">
                            ComplianceGPT can make mistakes. Consider checking important information.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
