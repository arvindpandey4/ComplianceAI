import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Dashboard.css';
import { API_BASE_URL } from '../config';

function Dashboard({ onLogout }) {
    const [user, setUser] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [showUpload, setShowUpload] = useState(true);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const [chatHistory, setChatHistory] = useState([]);

    const [isDemoSession, setIsDemoSession] = useState(false);

    const [showDropdown, setShowDropdown] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [settingsForm, setSettingsForm] = useState({
        full_name: '',
        agent_persona: 'strict_formal'
    });

    // Fetch user and chat history on mount
    useEffect(() => {
        const userData = JSON.parse(localStorage.getItem('user'));
        setUser(userData);
        fetchChatHistory();

        // Fetch fresh user data to get persona
        fetchUserProfile();
    }, []);

    useEffect(() => {
        if (user) {
            setSettingsForm({
                full_name: user.full_name || '',
                agent_persona: user.agent_persona || 'strict_formal'
            });
        }
    }, [user, showSettings]);

    const fetchUserProfile = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/auth/me`, {
                headers: getAuthHeaders()
            });
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
        } catch (error) {
            console.error("Failed to fetch fresh user profile", error);
        }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.patch(`${API_BASE_URL}/auth/me`, settingsForm, {
                headers: getAuthHeaders()
            });
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
            setShowSettings(false);
            alert('Profile updated successfully!');
        } catch (error) {
            console.error('Update failed:', error);
            alert('Failed to update profile.');
        }
    };

    const handleViewDocument = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/query/knowledge/demo/pdf`, {
                headers: getAuthHeaders(),
                responseType: 'blob'
            });
            const file = new Blob([response.data], { type: 'application/pdf' });
            const fileURL = URL.createObjectURL(file);
            window.open(fileURL, '_blank');
        } catch (error) {
            console.error('Error viewing document:', error);
            alert('Failed to load demo document.');
        }
    };

    const fetchChatHistory = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/query/history/sessions`, {
                headers: getAuthHeaders()
            });
            setChatHistory(response.data);
        } catch (error) {
            console.error('Failed to fetch chat history', error);
        }
    };

    const handleSelectSession = async (id) => {
        if (id === sessionId) return;

        setIsLoading(true);
        try {
            const response = await axios.get(`${API_BASE_URL}/query/history/${id}`, {
                headers: getAuthHeaders()
            });

            setMessages(response.data);
            setSessionId(id);
            setShowUpload(false);
        } catch (error) {
            console.error('Failed to load session', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewChat = () => {
        setSessionId(null);
        setMessages([]);
        setShowUpload(true);
        setIsDemoSession(false);
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Authorization': `Bearer ${token}`
        };
    };

    const handleFileUpload = async (files) => {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            await axios.post(`${API_BASE_URL}/ingest/`, formData, {
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'multipart/form-data'
                }
            });

            setUploadedFiles(prev => [...prev, ...Array.from(files).map(f => f.name)]);
            setShowUpload(false);

            // Add system message
            setMessages(prev => [...prev, {
                role: 'system',
                content: `Successfully uploaded ${files.length} document(s). You can now ask questions about them.`
            }]);
        } catch (error) {
            console.error('Upload failed:', error);
            setMessages(prev => [...prev, {
                role: 'system',
                content: 'Upload failed. Please try again.'
            }]);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage = inputValue.trim();
        setInputValue('');

        // Add user message
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await axios.post(
                `${API_BASE_URL}/query/`,
                {
                    query: userMessage,
                    session_id: sessionId
                },
                { headers: getAuthHeaders() }
            );

            const { session_id: newSessionId, data } = response.data;

            // If starting a new session, update list
            if (!sessionId) {
                setSessionId(newSessionId);
                fetchChatHistory(); // Refresh list to show new session
            }

            // Add assistant message
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.response,
                status: data.status,
                reasoning: data.reasoning,
                sources: data.sources,
                followUpQuestions: data.follow_up_questions
            }]);
        } catch (error) {
            console.error('Query failed:', error);
            setMessages(prev => [...prev, {
                role: 'system',
                content: 'Failed to get response. Please try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFollowUpClick = (question) => {
        setInputValue(question);
    };

    return (
        <div className="dashboard-container">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left" onClick={handleNewChat} style={{ cursor: 'pointer' }}>
                    <div className="logo-badge">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div>
                        <h1>ComplianceAI</h1>
                        <p className="header-subtitle">Regulatory Compliance Assistant</p>
                    </div>
                </div>

                <div className="header-right">
                    {isDemoSession && (
                        <button onClick={handleViewDocument} className="btn-view-doc">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            View Document
                        </button>
                    )}
                    <div className="user-menu-container">
                        <div className="user-info" onClick={() => setShowDropdown(!showDropdown)}>
                            <div className="user-avatar">
                                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <span className="user-name">{user?.full_name || 'User'}</span>
                            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style={{ marginLeft: 8, opacity: 0.7 }}>
                                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </div>

                        {showDropdown && (
                            <>
                                <div
                                    style={{ position: 'fixed', inset: 0, zIndex: 90 }}
                                    onClick={() => setShowDropdown(false)}
                                />
                                <div className="user-dropdown">
                                    <button className="dropdown-item" onClick={() => { setShowDropdown(false); setShowSettings(true); }}>
                                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" /></svg>
                                        Profile Settings
                                    </button>
                                    <button className="dropdown-item logout" onClick={onLogout}>
                                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V4a1 1 0 00-1-1H3zm11 4.414l-4.293 4.293a1 1 0 01-1.414 0L4 7.414 5.414 6l3.293 3.293L13.586 6 15 7.414z" clipRule="evenodd" /></svg>
                                        Logout
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </header>

            <div className="dashboard-layout">
                {/* Sidebar */}
                <aside className="dashboard-sidebar">
                    <button onClick={handleNewChat} className="btn-new-chat">
                        <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
                            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                        </svg>
                        New Chat
                    </button>

                    <div className="sidebar-title">Recent History</div>
                    <div className="history-list">
                        {chatHistory.map((item) => (
                            <div
                                key={item.session_id}
                                className={`history-item ${sessionId === item.session_id ? 'active' : ''}`}
                                onClick={() => handleSelectSession(item.session_id)}
                                title={item.preview}
                            >
                                {item.preview}
                            </div>
                        ))}
                    </div>
                </aside>

                {/* Main Content */}
                <main className="dashboard-main">
                    {showUpload && messages.length === 0 ? (
                        /* Upload Area */
                        <div className="upload-section">
                            <div
                                className={`upload-zone ${isDragging ? 'dragging' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <div className="upload-icon">
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M7 18C5.17107 18.4117 4 19.0443 4 19.7537C4 20.9943 7.58172 22 12 22C16.4183 22 20 20.9943 20 19.7537C20 19.0443 18.8289 18.4117 17 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <path d="M12 15V3M12 3L16 7M12 3L8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                </div>
                                <h2>Upload Compliance Documents</h2>
                                <p>Drag and drop PDF files here, or click to browse</p>
                                <div className="upload-hint">
                                    Supported formats: PDF • Max size: 10MB per file
                                </div>
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                multiple
                                accept=".pdf"
                                style={{ display: 'none' }}
                                onChange={(e) => handleFileUpload(e.target.files)}
                            />

                            {/* Demo Document Button */}
                            <div className="demo-document">
                                <div className="demo-divider">
                                    <span>OR</span>
                                </div>
                                <button
                                    className="btn-demo"
                                    onClick={() => {
                                        setShowUpload(false);
                                        setIsDemoSession(true);
                                        setMessages([{
                                            role: 'system',
                                            content: 'Demo document loaded: "Compliance Auditing Guidelines – C&AG of India". You can now ask questions about compliance auditing!'
                                        }, {
                                            role: 'assistant',
                                            content: 'Welcome! I\'ve loaded the Compliance Auditing Guidelines. Here are some questions you can ask:',
                                            followUpQuestions: [
                                                'What are the key principles of compliance auditing?',
                                                'What is the role of internal controls in compliance auditing?',
                                                'How should auditors assess compliance with laws and regulations?'
                                            ]
                                        }]);
                                    }}
                                >
                                    <svg viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
                                    </svg>
                                    Try Demo: Compliance Auditing Guidelines – C&AG of India
                                </button>
                                <p className="demo-hint">Pre-loaded document ready to explore</p>
                            </div>

                            {uploadedFiles.length > 0 && (
                                <div className="uploaded-files">
                                    <h3>Uploaded Documents</h3>
                                    <ul>
                                        {uploadedFiles.map((file, idx) => (
                                            <li key={idx}>
                                                <svg viewBox="0 0 20 20" fill="currentColor">
                                                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                                                </svg>
                                                {file}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* Chat Interface */
                        <div className="chat-container">
                            <div className="messages-area">
                                {messages.length === 0 && (
                                    <div className="empty-state">
                                        <div className="empty-icon">💬</div>
                                        <h2>Start a Conversation</h2>
                                        <p>Ask questions about your compliance documents</p>
                                    </div>
                                )}

                                {messages.map((msg, idx) => (
                                    <div key={idx} className={`message message-${msg.role}`}>
                                        {msg.role === 'user' && (
                                            <div className="message-avatar user-avatar-small">
                                                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                                            </div>
                                        )}
                                        {msg.role === 'assistant' && (
                                            <div className="message-avatar bot-avatar">
                                                <svg viewBox="0 0 24 24" fill="currentColor">
                                                    <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                                                    <path d="M2 17L12 22L22 17" />
                                                    <path d="M2 12L12 17L22 12" />
                                                </svg>
                                            </div>
                                        )}

                                        <div className="message-content">
                                            {msg.role === 'system' && (
                                                <div className="system-badge">System</div>
                                            )}
                                            <div className="message-text">{msg.content}</div>

                                            {msg.status && (
                                                <div className={`status-badge status-${msg.status.toLowerCase().replace(' ', '-')}`}>
                                                    {msg.status}
                                                </div>
                                            )}

                                            {msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                                                <div className="followup-questions">
                                                    <p className="followup-label">Suggested questions:</p>
                                                    {msg.followUpQuestions.map((q, i) => (
                                                        <button
                                                            key={i}
                                                            className="followup-btn"
                                                            onClick={() => handleFollowUpClick(q)}
                                                        >
                                                            {q}
                                                        </button>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}

                                {isLoading && (
                                    <div className="message message-assistant">
                                        <div className="message-avatar bot-avatar">
                                            <svg viewBox="0 0 24 24" fill="currentColor">
                                                <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                                            </svg>
                                        </div>
                                        <div className="message-content">
                                            <div className="typing-indicator">
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="input-area">
                                <form onSubmit={handleSubmit} className="input-form">
                                    <button
                                        type="button"
                                        className="btn-upload-more"
                                        onClick={() => setShowUpload(true)}
                                        title="Upload more documents"
                                    >
                                        <svg viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                    <input
                                        type="text"
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        placeholder="Ask a compliance question..."
                                        disabled={isLoading}
                                        className="chat-input"
                                    />
                                    <button
                                        type="submit"
                                        disabled={!inputValue.trim() || isLoading}
                                        className="btn-send"
                                    >
                                        <svg viewBox="0 0 20 20" fill="currentColor">
                                            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                                        </svg>
                                    </button>
                                </form>
                            </div>
                        </div>
                    )}
                </main>
            </div>

            {/* Settings Modal */}
            {showSettings && (
                <div className="modal-overlay" onClick={() => setShowSettings(false)}>
                    <div className="settings-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Profile Settings</h2>
                            <button className="btn-close" onClick={() => setShowSettings(false)}>&times;</button>
                        </div>

                        <form onSubmit={handleUpdateProfile}>
                            <div className="form-group">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    value={settingsForm.full_name}
                                    onChange={e => setSettingsForm({ ...settingsForm, full_name: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label>Email Address</label>
                                <input
                                    type="email"
                                    value={user?.email || ''}
                                    disabled
                                />
                            </div>

                            <div className="form-group">
                                <label>Agent Persona (Compliance Auditor)</label>
                                <select
                                    value={settingsForm.agent_persona}
                                    onChange={e => setSettingsForm({ ...settingsForm, agent_persona: e.target.value })}
                                >
                                    <option value="strict_formal">Strict & Formal (Default)</option>
                                    <option value="educational">Educational & Explanatory</option>
                                    <option value="risk_focused">Risk-Focused</option>
                                    <option value="concise">Concise & Actionable</option>
                                </select>
                            </div>

                            <div className="modal-actions">
                                <button type="button" className="btn-cancel" onClick={() => setShowSettings(false)}>Cancel</button>
                                <button type="submit" className="btn-save">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
