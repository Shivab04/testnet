import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import axios from 'axios';
import { io } from 'socket.io-client';
import toast, { Toaster } from 'react-hot-toast';
import { 
  Users, 
  Search, 
  MessageCircle, 
  Settings, 
  User, 
  Crown,
  Send,
  LogOut,
  Menu,
  X,
  Calendar,
  Clock,
  Trash2,
  Plus
} from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/users/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUser();
      toast.success('Login successful!');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
      return false;
    }
  };

  const register = async (name, email, password, role = 'seeker') => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        name,
        email,
        password,
        role
      });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUser();
      toast.success('Registration successful!');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    toast.success('Logged out successfully');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Navbar = () => {
  const { user, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-white">
              Testnet
            </Link>
          </div>
          
          {user && (
            <div className="hidden md:flex items-center space-x-4">
              <Link to="/dashboard" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Dashboard
              </Link>
              <Link to="/search" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Find Mentors
              </Link>
              <Link to="/chat" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Chat
              </Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="text-yellow-400 hover:text-yellow-300 px-3 py-2 rounded-md text-sm font-medium">
                  Admin
                </Link>
              )}
              <div className="text-gray-300 px-3 py-2">
                {user.name} ({user.role})
              </div>
              <button
                onClick={logout}
                className="text-gray-300 hover:text-white p-2 rounded-md"
              >
                <LogOut size={20} />
              </button>
            </div>
          )}
          
          {user && (
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-300 hover:text-white p-2 rounded-md"
              >
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          )}
        </div>
      </div>
      
      {isMenuOpen && user && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-800">
            <Link to="/dashboard" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">
              Dashboard
            </Link>
            <Link to="/search" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">
              Find Mentors
            </Link>
            <Link to="/chat" className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium">
              Chat
            </Link>
            {user.role === 'admin' && (
              <Link to="/admin" className="text-yellow-400 hover:text-yellow-300 block px-3 py-2 rounded-md text-base font-medium">
                Admin
              </Link>
            )}
            <div className="text-gray-300 px-3 py-2">
              {user.name} ({user.role})
            </div>
            <button
              onClick={logout}
              className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'seeker'
  });
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) {
      await login(formData.email, formData.password);
    } else {
      await register(formData.name, formData.email, formData.password, formData.role);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            {isLogin ? 'Welcome back to Testnet' : 'Join the Testnet community'}
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            {!isLogin && (
              <div>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Full name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>
            )}
            
            <div>
              <input
                id="email"
                name="email"
                type="email"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm ${
                  isLogin ? 'rounded-t-md' : ''
                }`}
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            
            <div>
              <input
                id="password"
                name="password"
                type="password"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm ${
                  isLogin ? 'rounded-b-md' : ''
                }`}
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
            
            {!isLogin && (
              <div>
                <select
                  id="role"
                  name="role"
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-700 placeholder-gray-500 text-white bg-gray-800 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  value={formData.role}
                  onChange={handleChange}
                >
                  <option value="seeker">Seeker</option>
                  <option value="mentor">Mentor</option>
                </select>
              </div>
            )}
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {isLogin ? 'Sign in' : 'Sign up'}
            </button>
          </div>
          
          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-indigo-400 hover:text-indigo-300 text-sm"
            >
              {isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/users/me/profile`);
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-white mb-6">Dashboard</h1>
            
            {/* Hero Section */}
            <div className="mb-8 relative">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 text-white">
                <div 
                  className="absolute inset-0 bg-cover bg-center rounded-lg opacity-20"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1552508744-1696d4464960?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxtZW50b3Jpbmd8ZW58MHx8fGJsYWNrfDE3NTI4NTc1ODN8MA&ixlib=rb-4.1.0&q=85")'
                  }}
                ></div>
                <div className="relative z-10">
                  <h2 className="text-3xl font-bold mb-2">Welcome back, {user.name}!</h2>
                  <p className="text-xl opacity-90">
                    {user.role === 'seeker' && 'Find your perfect mentor today'}
                    {user.role === 'mentor' && 'Help others achieve their goals'}
                    {user.role === 'admin' && 'Manage the Testnet community'}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Link to="/search" className="bg-gray-700 hover:bg-gray-600 rounded-lg p-6 text-center transition-colors">
                <Search className="mx-auto mb-4 text-indigo-400" size={32} />
                <h3 className="text-lg font-medium text-white mb-2">Find Mentors</h3>
                <p className="text-gray-300">Discover experts in your field</p>
              </Link>
              
              <Link to="/chat" className="bg-gray-700 hover:bg-gray-600 rounded-lg p-6 text-center transition-colors">
                <MessageCircle className="mx-auto mb-4 text-green-400" size={32} />
                <h3 className="text-lg font-medium text-white mb-2">Chat</h3>
                <p className="text-gray-300">Connect with your mentors</p>
              </Link>
              
              <Link to="/profile" className="bg-gray-700 hover:bg-gray-600 rounded-lg p-6 text-center transition-colors">
                <User className="mx-auto mb-4 text-purple-400" size={32} />
                <h3 className="text-lg font-medium text-white mb-2">Profile</h3>
                <p className="text-gray-300">Update your information</p>
              </Link>
            </div>

            {/* Profile Summary */}
            {profile && (
              <div className="bg-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-medium text-white mb-4">Profile Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-300"><span className="font-medium">Role:</span> {user.role}</p>
                    <p className="text-gray-300"><span className="font-medium">Status:</span> {user.is_verified ? 'Verified' : 'Pending'}</p>
                    {profile.bio && (
                      <p className="text-gray-300 mt-2"><span className="font-medium">Bio:</span> {profile.bio}</p>
                    )}
                  </div>
                  <div>
                    {profile.skills && profile.skills.length > 0 && (
                      <div>
                        <p className="text-gray-300 font-medium mb-2">Skills:</p>
                        <div className="flex flex-wrap gap-2">
                          {profile.skills.map((skill, index) => (
                            <span key={index} className="bg-indigo-600 text-white px-2 py-1 rounded-full text-sm">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/search/mentors?q=${encodeURIComponent(searchQuery)}`);
      setMentors(response.data);
    } catch (error) {
      console.error('Error searching mentors:', error);
      toast.error('Failed to search mentors');
    } finally {
      setLoading(false);
    }
  };

  const startChat = async (mentorId) => {
    try {
      const response = await axios.post(`${API}/conversations`, null, {
        params: { mentor_id: mentorId }
      });
      toast.success('Chat started successfully!');
      // Navigate to chat page with conversation ID
      window.location.href = `/chat?conversation=${response.data.id}`;
    } catch (error) {
      console.error('Error starting chat:', error);
      toast.error('Failed to start chat');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-white mb-6">Find Mentors</h1>
            
            {/* Search Form */}
            <form onSubmit={handleSearch} className="mb-8">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for mentors by skills, experience, or keywords..."
                  className="flex-1 px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </form>

            {/* Results */}
            {mentors.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mentors.map((mentor) => (
                  <div key={mentor.user.id} className="bg-gray-700 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-medium text-white">{mentor.user.name}</h3>
                        <p className="text-gray-300 text-sm">
                          {mentor.profile.experience_years} years experience
                        </p>
                        {mentor.user.is_verified && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                            Verified
                          </span>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-indigo-400 font-medium">
                          ${mentor.profile.hourly_rate}/hr
                        </p>
                        <p className="text-gray-400 text-sm">
                          Match: {mentor.score}%
                        </p>
                      </div>
                    </div>
                    
                    {mentor.profile.bio && (
                      <p className="text-gray-300 text-sm mb-4">{mentor.profile.bio}</p>
                    )}
                    
                    {mentor.profile.skills && mentor.profile.skills.length > 0 && (
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-2">
                          {mentor.profile.skills.slice(0, 3).map((skill, index) => (
                            <span key={index} className="bg-indigo-600 text-white px-2 py-1 rounded-full text-xs">
                              {skill}
                            </span>
                          ))}
                          {mentor.profile.skills.length > 3 && (
                            <span className="text-gray-400 text-xs">
                              +{mentor.profile.skills.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <button
                      onClick={() => startChat(mentor.user.id)}
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      Start Chat
                    </button>
                  </div>
                ))}
              </div>
            )}

            {searchQuery && mentors.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-gray-400">No mentors found matching your search.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatPage = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchConversations();
    
    // Initialize socket
    const newSocket = io(BACKEND_URL);
    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  useEffect(() => {
    if (socket && selectedConversation) {
      socket.emit('join_room', { room: selectedConversation.id });
      
      socket.on('receive_message', (message) => {
        setMessages(prev => [...prev, message]);
      });

      return () => {
        socket.emit('leave_room', { room: selectedConversation.id });
        socket.off('receive_message');
      };
    }
  }, [socket, selectedConversation]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`${API}/conversations/${conversationId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.id);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      await axios.post(`${API}/messages`, {
        conversation_id: selectedConversation.id,
        content: newMessage
      });
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* Sidebar */}
      <div className="w-1/3 bg-gray-800 border-r border-gray-700">
        <div className="p-4">
          <h2 className="text-xl font-bold text-white mb-4">Conversations</h2>
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedConversation?.id === conversation.id
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <div className="font-medium">
                  Conversation {conversation.id.slice(-8)}
                </div>
                <div className="text-sm opacity-75">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="bg-gray-800 border-b border-gray-700 p-4">
              <h3 className="text-lg font-medium text-white">
                Chat - {selectedConversation.id.slice(-8)}
              </h3>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.sender_id === user.id ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender_id === user.id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300'
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(message.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="bg-gray-800 border-t border-gray-700 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="mx-auto mb-4 text-gray-600" size={48} />
              <p className="text-gray-400">Select a conversation to start chatting</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const AdminPage = () => {
  const [mentors, setMentors] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchMentors();
    }
  }, [user]);

  const fetchMentors = async () => {
    try {
      const response = await axios.get(`${API}/admin/mentors`);
      setMentors(response.data);
    } catch (error) {
      console.error('Error fetching mentors:', error);
    }
  };

  const verifyMentor = async (mentorId) => {
    try {
      await axios.put(`${API}/admin/mentors/${mentorId}/verify`);
      toast.success('Mentor verified successfully!');
      fetchMentors();
    } catch (error) {
      console.error('Error verifying mentor:', error);
      toast.error('Failed to verify mentor');
    }
  };

  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center mb-6">
              <Crown className="text-yellow-400 mr-3" size={32} />
              <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-medium text-white mb-4">Mentor Management</h2>
              
              <div className="space-y-4">
                {mentors.map((mentor) => (
                  <div key={mentor.user.id} className="bg-gray-600 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-white">{mentor.user.name}</h3>
                        <p className="text-gray-300">{mentor.user.email}</p>
                        <div className="flex items-center mt-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            mentor.user.is_verified 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {mentor.user.is_verified ? 'Verified' : 'Pending'}
                          </span>
                          <span className="ml-2 text-gray-400 text-sm">
                            Registered: {new Date(mentor.user.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        {mentor.profile && (
                          <div className="mb-2">
                            <p className="text-gray-300">
                              {mentor.profile.experience_years} years experience
                            </p>
                            <p className="text-indigo-400">
                              ${mentor.profile.hourly_rate}/hr
                            </p>
                          </div>
                        )}
                        
                        {!mentor.user.is_verified && (
                          <button
                            onClick={() => verifyMentor(mentor.user.id)}
                            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                          >
                            Verify
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {mentor.profile && mentor.profile.bio && (
                      <div className="mt-4">
                        <p className="text-gray-300 text-sm">{mentor.profile.bio}</p>
                      </div>
                    )}
                    
                    {mentor.profile && mentor.profile.skills && mentor.profile.skills.length > 0 && (
                      <div className="mt-4">
                        <div className="flex flex-wrap gap-2">
                          {mentor.profile.skills.map((skill, index) => (
                            <span key={index} className="bg-indigo-600 text-white px-2 py-1 rounded-full text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-900">
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<ProtectedRoute redirectTo="/dashboard"><LoginPage /></ProtectedRoute>} />
            <Route path="/" element={<ProtectedRoute><><Navbar /><Dashboard /></></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><><Navbar /><Dashboard /></></ProtectedRoute>} />
            <Route path="/search" element={<ProtectedRoute><><Navbar /><SearchPage /></></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><><Navbar /><ChatPage /></></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute><><Navbar /><AdminPage /></></ProtectedRoute>} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

const ProtectedRoute = ({ children, redirectTo = "/login" }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }
  
  if (!user && redirectTo !== "/dashboard") {
    return <Navigate to={redirectTo} replace />;
  }
  
  if (user && redirectTo === "/dashboard") {
    return <Navigate to={redirectTo} replace />;
  }
  
  return children;
};

export default App;