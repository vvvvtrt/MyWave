import React, { useState, useEffect } from "react";
import { api } from "./api";
import { Camera, MapPin, Heart, MessageCircle, Share2, Home, Users, Plus, Search, Menu, Eye, EyeOff, Sun, Moon, X } from "lucide-react";
import { MiniMap as MapComponent, MapModal } from "./components/Map";

export default function App() {
  const [query, setQuery] = useState("");
  // Feed LLM chat (mock)
  const [showLLMChat, setShowLLMChat] = useState(false);
  const [llmMessages, setLlmMessages] = useState<any[]>([]);
  const [llmInput, setLlmInput] = useState("");
  const [posts, setPosts] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("feed");
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  // const [scrollY, setScrollY] = useState(0);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [chats, setChats] = useState<any[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatsLoading, setChatsLoading] = useState(false);
  // Places suggestions from backend
  const [places, setPlaces] = useState<any[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<any | null>(null);
  const [showSurvey, setShowSurvey] = useState(false);
  const [surveyQuestions, setSurveyQuestions] = useState<any[]>([]);
  const [surveyAnswers, setSurveyAnswers] = useState<Record<string,string>>({});
  const [showMapModal, setShowMapModal] = useState(false);
  const [mapPoints, setMapPoints] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.posts.list();
        console.log('Posts data:', data);
        setPosts(data as any);
      } catch (e) {
        console.error('Error loading posts:', e);
        setPosts([]);
      } finally {
      setLoading(false);
    }
    })();
  }, []);
  useEffect(() => {
    (async () => {
      try {
        const list = await api.places.list();
        setPlaces(list as any);
      } catch (e) {
        console.error('Error loading places:', e);
        setPlaces([]);
      }
    })();
  }, []);

  async function handleFeedSearch() {
    try {
      const res = await api.search(query);
      setPosts(res as any);
    } catch (e) {
      console.error('Error searching:', e);
      setPosts([]);
    } finally {
      // Show mock LLM chat below the search
      setShowLLMChat(true);
      setLlmMessages([
        { id: Date.now(), author: 'Моя Волна', text: 'Привет! Я помогу подобрать приключение. Спроси, что хочешь испытать.', created_at: new Date().toISOString() },
      ]);
    }
  }

  function handleLLMSend() {
    const text = llmInput.trim();
    if (!text) return;
    const userMsg = { id: Date.now(), author: currentUser?.username || 'Вы', text, created_at: new Date().toISOString() };
    setLlmMessages(prev => [...prev, userMsg]);
    setLlmInput("");
    // Mock LLM reply
    const reply = { id: Date.now()+1, author: 'Моя Волна', text: 'Это ответ-заглушка от LLM 🙂 Скоро здесь будет умный помощник.', created_at: new Date().toISOString() };
    setTimeout(() => setLlmMessages(prev => [...prev, reply]), 300);
  }

  // Load chats when switching to groups
  useEffect(() => {
    (async () => {
      if (activeTab !== 'groups') return;
      setChatsLoading(true);
      try {
        const list = await api.chats.list();
        setChats(list as any);
        if (list && (list as any).length > 0) {
          const currentId = selectedChatId ?? (list as any)[0].id;
          setSelectedChatId(currentId);
          const msgs = await api.chats.messages(currentId);
          setChatMessages(msgs as any);
        } else {
          setSelectedChatId(null);
          setChatMessages([]);
        }
      } catch (e) {
        console.error('Error loading chats:', e);
        setChats([]);
        setSelectedChatId(null);
        setChatMessages([]);
      } finally {
        setChatsLoading(false);
      }
    })();
  }, [activeTab]);

  async function handleSelectChat(chatId: number) {
    try {
      setSelectedChatId(chatId);
      const msgs = await api.chats.messages(chatId);
      setChatMessages(msgs as any);
    } catch (e) {
      console.error('Error loading messages:', e);
      setChatMessages([]);
    }
  }

  async function handleSendMessage() {
    const text = chatInput.trim();
    if (!text || !selectedChatId) return;
    try {
      const msg = await api.chats.send(selectedChatId, text);
      setChatMessages((prev: any[]) => [...prev, msg as any]);
      setChatInput("");
    } catch (e) {
      console.error('Error sending message:', e);
      // local fallback
      setChatMessages((prev: any[]) => [...prev, { id: Date.now(), text, author: currentUser?.username || 'Вы', created_at: new Date().toISOString() }]);
      setChatInput("");
    }
  }

  // useEffect(() => {
  //   const handleScroll = () => setScrollY(window.scrollY);
  //   window.addEventListener('scroll', handleScroll);
  //   return () => window.removeEventListener('scroll', handleScroll);
  // }, []);

  async function handleLike(postId: any) {
    try {
      const updated = await api.posts.like(postId);
      // Ensure the updated post has the correct format
      const formattedPost = {
        id: updated.id,
        title: updated.title,
        description: updated.description || "",
        author: updated.author || "Пользователь",
        likes: updated.likes || 0,
        liked: updated.liked || false,
        comments: updated.comments || [],
        photos: updated.photos || [],
        route: updated.route || []
      };
      setPosts((prev: any[]) => prev.map((p: any) => p.id === postId ? formattedPost : p));
    } catch (e) {
      console.error('Error liking post:', e);
      // Fallback: just toggle the liked state locally
      setPosts((prev: any[]) => prev.map((p: any) => 
        p.id === postId ? { ...p, liked: !p.liked, likes: p.liked ? p.likes - 1 : p.likes + 1 } : p
      ));
    }
  }

  async function handleAddComment(postId: any, text: string) {
    if (!text) return;
    try {
      const c = await api.comments.add({ post_id: postId, text });
      // Ensure the comment has the correct format
      const formattedComment = {
        id: c.id,
        text: c.text,
        author: c.author || "Пользователь"
      };
      setPosts((prev: any[]) => prev.map((p: any) => p.id === postId ? {...p, comments:[...p.comments, formattedComment]} : p));
    } catch (e) {
      console.error('Error adding comment:', e);
      // Fallback: add comment locally
      const localComment = {
        id: Date.now(),
        text: text,
        author: currentUser?.username || 'Вы'
      };
      setPosts((prev: any[]) => prev.map((p: any) => 
        p.id === postId ? {...p, comments: [...p.comments, localComment]} : p
      ));
    }
  }

  async function handleCreateAdventure() {
    setShowCreatePost(true);
  }

  async function handleCreatePost(postData: any) {
    try {
      const created = await api.posts.create(postData);
      setPosts((prev: any[]) => [created as any, ...prev]);
      setShowCreatePost(false);
      setActiveTab('my');
    } catch (e) {
      console.error('Error creating post:', e);
      // Fallback: add post locally
      const localPost = {
        id: Date.now(),
        title: postData.title,
        description: postData.description,
        author: currentUser?.username || 'Вы',
        likes: 0,
        liked: false,
        comments: [],
        photos: postData.photos || [],
        route: []
      };
      setPosts((prev: any[]) => [localPost, ...prev]);
      setShowCreatePost(false);
      setActiveTab('my');
    }
  }

  function handleStartJourneyFromPlace(place: any) {
    const payload = { title: place.name, description: place.description, photos: [place.image] } as any;
    handleCreatePost(payload);
    setActiveTab('my');
  }

  async function handleTravelWithSomeone(place: any) {
    try {
      const created = await api.chats.create(place?.name || 'Путешествие');
      setActiveTab('groups');
      setSelectedChatId(created.id);
      try {
        const msgs = await api.chats.messages(created.id);
        setChatMessages(msgs as any);
      } catch {}
    } catch (e) {
      console.error('Error creating chat:', e);
      setActiveTab('groups');
    }
  }

  async function handleAuth(credentials: any) {
    try {
      let response;
      if (credentials.mode === 'register') {
        // Преобразуем данные для регистрации
        const registerData = {
          email: credentials.email,
          username: credentials.name,
          password: credentials.password,
          full_name: credentials.name
        };
        response = await api.register(registerData);
      } else {
        // Для входа используем email как username
        const loginData = {
          email: credentials.email,
          password: credentials.password
        };
        response = await api.login(loginData);
      }
      
      // Сохраняем токен
      localStorage.setItem('token', response.access_token);
      
      // Получаем информацию о пользователе
      const userInfo = await api.getCurrentUser();
      setCurrentUser(userInfo);
      setIsAuthenticated(true);

      // After auth, check survey status
      try {
        const status = await api.survey.status();
        if (!status.completed) {
          const q = await api.survey.questions();
          setSurveyQuestions(q.questions || []);
          setShowSurvey(true);
        }
      } catch (e) {
        // ignore
      }

      // Load recommendations
      try {
        const recPosts = await api.recs.list();
        if (Array.isArray(recPosts) && recPosts.length > 0) {
          setPosts(recPosts as any);
        }
      } catch (e) {
        // ignore
      }
    } catch (e) {
      console.error(e);
    }
  }

  if (loading) {
    return <SeaLoading />;
  }

  if (!isAuthenticated) {
    return (
      <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen relative overflow-hidden">
        <AnimatedBackground />
        <div className="relative z-10 min-h-screen flex items-center justify-center p-6">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <div className="flex justify-end mb-4">
                <button
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className="p-2 rounded-lg bg-white/80 border border-gray-200/80 text-slate-700 hover:bg-white/90 transition-colors backdrop-blur-sm dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:hover:bg-slate-700"
                  aria-label="Toggle theme"
                >
                  {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">Моя волна</h1>
              <p className="text-white/80">Исследуй, приглашай, запоминай</p>
            </div>
            <AuthForm onAuth={handleAuth} />
          </div>
        </div>
      </div>
      </div>
    );
  }

  // const headerHeight = Math.max(100, 300 - scrollY * 0.5);
  // const isHeaderCollapsed = scrollY > 200;

  return (
    <div className={isDarkMode ? 'dark' : ''}>
    <div className="min-h-screen relative overflow-hidden">
      <AnimatedBackground />
      
      <div className="relative z-10">
        {/* Header */}
        <header className="sticky top-0 z-40 p-4 md:p-8">
          <div className="w-full max-w-[120rem] mx-auto backdrop-blur-md bg-white/25 border border-gray-200/25 rounded-2xl p-4 shadow-lg text-slate-900 dark:bg-black/25 dark:border-black/25 dark:text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 w-full">
                <button 
                  onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                  className="md:hidden p-2 rounded-lg bg-white border border-gray-200 text-slate-700 hover:bg-gray-100 transition-colors dark:backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35"
                >
                  <Menu className="w-5 h-5 text-white" />
                </button>
                
                <h1>Моя Волна</h1>


              </div>
              
              <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="@никнейм"
                    onKeyDown={async (e)=>{ const t=(e.target as HTMLInputElement); if((e as any).key==='Enter' && t.value.trim()){ try{ const uname=t.value.trim().replace(/^@/, ''); const dm=await api.chats.createDM(uname); setActiveTab('groups'); setSelectedChatId(dm.id); try{ const msgs=await api.chats.messages(dm.id); setChatMessages(msgs as any);}catch{} t.value=''; }catch(err){ console.error('DM error', err);} } }}
                    className="rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none text-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                  />
                </div>
                <button
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className="p-2 rounded-lg bg-white border border-gray-200 text-slate-700 hover:bg-gray-100 transition-colors dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:hover:bg-slate-700"
                  aria-label="Toggle theme"
                >
                  {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
                <button 
                  onClick={() => setShowProfile(true)}
                  className="hidden sm:flex items-center gap-2 rounded-full px-4 py-2 bg-white border border-gray-200 text-slate-700 hover:bg-white/90 transition-colors dark:backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center font-bold text-white text-sm">
                    {currentUser?.username?.[0] || 'U'}
                  </div>
                  <span className="text-slate-700 text-sm dark:text-white">{currentUser?.username || 'Пользователь'}</span>
                </button>
                <button 
                  onClick={() => setIsAuthenticated(false)}
                  className="px-4 py-2 rounded-full bg-white border border-gray-200 text-slate-700 hover:bg-gray-100 transition-colors dark:backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35"
                >
                  Выход
                </button>
              </div>
            </div>
          </div>
        </header>


        <div className="flex max-w-[120rem] mx-auto">
          {/* Sidebar */}
          <aside className={`${sidebarCollapsed ? 'w-16' : 'w-72'} hidden md:block sticky top-[88px] h-[calc(100vh-88px)] p-6 transition-all duration-300`}>
            <div className="backdrop-blur-md bg-white/25 border border-gray-200/25 rounded-2xl p-4 shadow-lg text-slate-900 h-full dark:bg-black/25 dark:border-black/25 dark:text-white">
              {!sidebarCollapsed ? (
                <>
                  <nav className="space-y-2 text-sm">
                    <button onClick={() => setActiveTab('feed')} className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab==='feed' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/5 text-slate-700 dark:hover:bg-black/5 dark:text-white/80'} backdrop-blur-sm`}>
                      <Home className="w-5 h-5" />
                      Лента
                    </button>
                    <button onClick={() => setActiveTab('my')} className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab==='my' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/15 text-slate-700 dark:hover:bg-black/15 dark:text-white/80'} backdrop-blur-sm`}>
                      <Camera className="w-5 h-5" />
                      Мои путешествия
                    </button>
                    <button onClick={() => setActiveTab('groups')} className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab==='groups' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/15 text-slate-700 dark:hover:bg-black/15 dark:text-white/80'} backdrop-blur-sm`}>
                      <Users className="w-5 h-5" />
                      Мои группы
                    </button>
                  </nav>

                  <div className="mt-6">
                  <button onClick={handleCreateAdventure} className="w-full bg-orange-500 border border-orange-600 hover:bg-orange-600 text-white font-semibold px-4 py-3 rounded-xl shadow-lg flex items-center justify-center gap-2 transition-colors">
                      <Plus className="w-5 h-5" />
                      Создать
                    </button>
                  </div>
                </>
              ) : (
                <nav className="space-y-4 flex flex-col items-center">
                  <button onClick={() => setActiveTab('feed')} className={`p-3 rounded-xl transition-all ${activeTab==='feed' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/15 text-slate-700 dark:hover:bg-black/15 dark:text-white/80'} backdrop-blur-sm`}>
                    <Home className="w-5 h-5" />
                  </button>
                  <button onClick={() => setActiveTab('my')} className={`p-3 rounded-xl transition-all ${activeTab==='my' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/15 text-slate-700 dark:hover:bg-black/15 dark:text-white/80'} backdrop-blur-sm`}>
                    <Camera className="w-5 h-5" />
                  </button>
                  <button onClick={() => setActiveTab('groups')} className={`p-3 rounded-xl transition-all ${activeTab==='groups' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'hover:bg-white/15 text-slate-700 dark:hover:bg-black/15 dark:text-white/80'} backdrop-blur-sm`}>
                    <Users className="w-5 h-5" />
                  </button>
                  <button onClick={handleCreateAdventure} className="p-3 rounded-xl bg-orange-500 border border-orange-600 text-white hover:bg-orange-600 transition-colors">
                    <Plus className="w-5 h-5" />
                  </button>
                </nav>
              )}
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 p-4 md:p-6 pb-20">
            <div className="space-y-6">

              {(activeTab==='feed' || activeTab==='my') && (
                <>
                  {activeTab==='feed' && (
                <div className="backdrop-blur-md bg-white/25 border border-gray-200/25 rounded-2xl p-6 shadow-lg text-slate-900 dark:bg-black/25 dark:border-black/25 dark:text-white">
                <div className="text-center mb-6">
                  <h2 className="text-3xl font-bold text-slate-900 mb-2 dark:text-white">Чего хочется испытать сегодня?</h2>
                  <p className="text-slate-600 dark:text-white/70">Найди идеальное приключение для себя</p>
                </div>

                {/* Search */}
                <div className="flex gap-3 mb-3">
                  <input 
                    value={query} 
                    onChange={(e)=>setQuery(e.target.value)} 
                    placeholder="Кофе, прогулка у реки, старая книжная..." 
                    className="flex-1 rounded-2xl px-6 py-4 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none text-lg backdrop-blur-sm dark:backdrop-blur-md dark:bg-slate-900 dark:border-slate-700 dark:text-white" 
                  />
                  <button 
                          onClick={handleFeedSearch}
                    className="bg-orange-500 border border-orange-600 px-8 py-4 rounded-2xl font-semibold text-white shadow-lg hover:bg-orange-600 transition-colors"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                </div>

                {/* Category chips under search */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {['Популярные', 'Природа', 'Искусство', 'Еда', 'Спорт', 'Музыка', 'Книги', 'Путешествия'].map(suggestion => (
                    <button
                      key={suggestion}
                      onClick={() => setQuery(suggestion)}
                      className="px-4 py-2 rounded-full bg-white/25 border border-gray-200/25 text-slate-700 hover:bg-white/35 hover:border-gray-200/35 transition-colors text-sm backdrop-blur-sm dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:hover:bg-slate-700"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>

                {/* Places suggestions */}
                <div className="mt-4">
                  <h4 className="text-xl font-semibold mb-3">Предложения мест</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {places.map((p:any) => (
                      <button key={p.id} onClick={() => setSelectedPlace(p)} className="group text-left rounded-2xl overflow-hidden border border-gray-200/25 bg-white/10 dark:bg-black/20 hover:bg-white/15 dark:hover:bg-black/30 transition-colors">
                        <div className="aspect-video w-full overflow-hidden">
                          <img src={p.image} alt={p.name} className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform" />
                        </div>
                        <div className="p-3">
                          <div className="font-semibold text-sm">{p.name}</div>
                          <div className="text-xs text-slate-600 dark:text-white/70">{p.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                  
                  {/* Places Map */}
                  {places.length > 0 && (
                    <div className="mt-6">
                      <h5 className="text-lg font-semibold mb-3">Места на карте</h5>
                      <div className="rounded-2xl overflow-hidden border border-gray-200/25 bg-white/10 dark:bg-black/20">
                      <div style={{height: '300px'}}>
                        <MapComponent 
                          points={places.map((p: any, index: number) => ({
                            id: p.id || index,
                            name: p.name,
                            lat: 55.7558 + (Math.random() - 0.5) * 0.1, // Mock coordinates around Moscow
                            lng: 37.6173 + (Math.random() - 0.5) * 0.1,
                            description: p.description
                          }))}
                        />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                
                

                      {showLLMChat && (
                        <div className="mt-6 rounded-2xl border border-gray-200/25 bg-white/10 dark:bg-black/20 flex flex-col overflow-hidden">
                          <div className="p-3 border-b border-gray-200/25 dark:border-black/25 text-sm">Помощник • Моя Волна</div>
                          <div className="flex-1 p-3 space-y-3 max-h-[60vh] md:max-h-[65vh] overflow-y-auto">
                            {llmMessages.map((m:any)=> (
                              <div key={m.id} className="flex items-start gap-2">
                                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                                  {m.author?.[0] || 'U'}
                                </div>
                                <div className="flex-1 bg-white/25 border border-gray-200/25 rounded-xl px-3 py-2 text-slate-900 backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white">
                                  <div className="font-semibold text-slate-900 text-xs mb-1 dark:text-white">{m.author || 'Пользователь'}</div>
                                  <div className="text-slate-800 text-sm dark:text-white/90">{m.text}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="p-3 border-t border-gray-200/25 dark:border-black/25 flex gap-2">
                            <input
                              value={llmInput}
                              onChange={(e)=>setLlmInput(e.target.value)}
                              onKeyDown={(e)=>{ if((e as any).key==='Enter'){ (e as any).preventDefault(); handleLLMSend(); }}}
                              placeholder="Спросите помощника..."
                              className="flex-1 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors text-sm backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                            />
                            <button
                              onClick={handleLLMSend}
                              className="px-4 py-2 rounded-xl bg-orange-500 border border-orange-600 text-white font-semibold hover:bg-orange-600 transition-colors"
                            >
                              Отправить
                            </button>
                          </div>
                    </div>
                  )}
                    </div>
                  )}
                  {posts.filter((p: any) => activeTab==='my' ? p.author === (currentUser?.username || 'Вы') : true).map((post: any) => (
                    <AdventureCard 
                      key={post.id} 
                      post={{...post, route: post.route || sampleRoute(3)}} 
                      onLike={handleLike} 
                      onComment={handleAddComment}
                      onMapClick={(points) => {
                        setMapPoints(points);
                        setShowMapModal(true);
                      }}
                    />
                  ))}
                </>
              )}

              {activeTab === 'groups' && (
                <div className="backdrop-blur-md bg-white/25 border border-gray-200/25 p-4 md:p-6 rounded-3xl text-slate-900 dark:bg-black/25 dark:border-black/25 dark:text-white">
                  <h3 className="text-2xl font-semibold text-slate-900 mb-4 dark:text-white">Чаты</h3>
                  <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-2">
                    <div className="flex gap-2">
                      <input
                        id="create-group-input"
                        type="text"
                        placeholder="Название группы"
                        className="flex-1 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none text-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                      />
                      <button
                        onClick={async()=>{ const el=document.getElementById('create-group-input') as HTMLInputElement|null; const name=el?.value?.trim(); if(!name) return; try{ const g=await api.groups.create(name); const list=await api.chats.list(); setChats(list as any); setActiveTab('groups'); setSelectedChatId(g.id); const msgs=await api.chats.messages(g.id); setChatMessages(msgs as any); if(el) el.value=''; }catch(e){ console.error('Create group error', e);} }}
                        className="px-4 py-2 rounded-xl bg-orange-500 border border-orange-600 text-white text-sm font-semibold hover:bg-orange-600 transition-colors"
                      >
                        Создать группу
                      </button>
                    </div>
                    <div className="flex gap-2 md:col-span-2">
                      <input
                        id="add-user-id-input"
                        type="number"
                        placeholder="ID пользователя"
                        className="w-40 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none text-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                      />
                      <input
                        id="group-id-input"
                        type="number"
                        placeholder="ID группы"
                        className="w-40 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none text-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                      />
                      <button
                        onClick={async()=>{ const userEl=document.getElementById('add-user-id-input') as HTMLInputElement|null; const groupEl=document.getElementById('group-id-input') as HTMLInputElement|null; const userId=Number(userEl?.value||''); const groupId=Number(groupEl?.value||''); if(!userId || !groupId) return; try{ await api.groups.addMember(groupId, userId); if(groupEl) groupEl.value=''; if(userEl) userEl.value=''; }catch(e){ console.error('Add member error', e);} }}
                        className="px-4 py-2 rounded-xl bg-white/25 border border-gray-200/25 text-slate-700 text-sm hover:bg-white/35 transition-colors dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35"
                      >
                        Добавить участника
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-stretch md:h-[calc(100vh-88px-48px-48px-56px)]">
                    {/* Chats list */}
                    <div className="md:col-span-2 rounded-2xl border border-gray-200/25 bg-white/10 dark:bg-black/20 overflow-hidden">
                      <div className="p-3 border-b border-gray-200/25 dark:border-black/25 text-sm">Мои чаты</div>
                      <div className="h-full overflow-y-auto">
                        {chatsLoading && (
                          <div className="p-4 text-sm text-slate-600 dark:text-white/70">Загрузка...</div>
                        )}
                        {!chatsLoading && chats.length === 0 && (
                          <div className="p-4 text-sm text-slate-600 dark:text-white/70">Пока нет чатов</div>
                        )}
                        {chats.map((c: any) => (
                          <button
                            key={c.id}
                            onClick={() => handleSelectChat(c.id)}
                            className={`w-full text-left p-3 flex items-start gap-3 hover:bg-white/10 dark:hover:bg-black/25 transition-colors ${selectedChatId===c.id ? 'bg-white/10 dark:bg-black/30' : ''}`}
                          >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center font-bold text-white text-sm">
                              {c.name?.[0] || 'Ч'}
                      </div>
                            <div className="flex-1">
                              <div className="font-semibold text-sm">{c.name}</div>
                              {c.last_message && (
                                <div className="text-xs text-slate-600 dark:text-white/70 truncate">{c.last_message.text}</div>
                              )}
                            </div>
                          </button>
                    ))}
                  </div>
                </div>

                    {/* Messages pane */}
                    <div className="md:col-span-3 rounded-2xl border border-gray-200/25 bg-white/10 dark:bg-black/20 flex flex-col overflow-hidden h-full">
                      <div className="p-3 border-b border-gray-200/25 dark:border-black/25 text-sm">
                        {chats.find((c:any)=>c.id===selectedChatId)?.name || 'Выберите чат'}
                      </div>
                      <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                        {selectedChatId && chatMessages.map((m:any)=> (
                          <div key={m.id} className="flex items-start gap-2">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                              {m.author?.[0] || 'U'}
                            </div>
                            <div className="flex-1 bg-white/25 border border-gray-200/25 rounded-xl px-3 py-2 text-slate-900 backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white">
                              <div className="font-semibold text-slate-900 text-xs mb-1 dark:text-white">{m.author || 'Пользователь'}</div>
                              <div className="text-slate-800 text-sm dark:text-white/90">{m.text}</div>
                            </div>
                          </div>
                        ))}
                        {!selectedChatId && (
                          <div className="text-sm text-slate-600 dark:text-white/70">Выберите чат слева</div>
                        )}
                      </div>
                      <div className="p-3 border-t border-gray-200/25 dark:border-black/25 flex gap-2 sticky bottom-0 bg-white/10 dark:bg-black/20 backdrop-blur-md">
                        <input
                          value={chatInput}
                          onChange={(e)=>setChatInput(e.target.value)}
                          onKeyDown={(e)=>{ if((e as any).key==='Enter'){ (e as any).preventDefault(); handleSendMessage(); }}}
                          placeholder="Написать сообщение"
                          className="flex-1 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors text-sm backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                        />
                        <button
                          onClick={handleSendMessage}
                          className="px-4 py-2 rounded-xl bg-orange-500 border border-orange-600 text-white font-semibold hover:bg-orange-600 transition-colors"
                        >
                          Отправить
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>

        {/* Mobile bottom navigation */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 backdrop-blur-md bg-white/25 border-t border-gray-200/25 p-4 dark:bg-black/25 dark:border-black/25">
          <div className="flex justify-around">
            <button onClick={() => setActiveTab('feed')} className={`p-3 rounded-xl ${activeTab==='feed' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'text-slate-700 dark:text-white/70'} backdrop-blur-sm`}>
              <Home className="w-6 h-6" />
            </button>
            <button onClick={() => setActiveTab('my')} className={`p-3 rounded-xl ${activeTab==='my' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'text-slate-700 dark:text-white/70'} backdrop-blur-sm`}>
              <Camera className="w-6 h-6" />
            </button>
            <button onClick={handleCreateAdventure} className="p-3 rounded-xl bg-orange-500 border border-orange-600 text-white hover:bg-orange-600 transition-colors">
              <Plus className="w-6 h-6" />
            </button>
            <button onClick={() => setActiveTab('groups')} className={`p-3 rounded-xl ${activeTab==='groups' ? 'bg-white/25 text-orange-600 dark:bg-black/25 dark:text-orange-300' : 'text-slate-700 dark:text-white/70'} backdrop-blur-sm`}>
              <Users className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Place Suggestion Modal */}
      {selectedPlace && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setSelectedPlace(null)}></div>
          <div className="relative bg-white/25 border border-gray-200/25 rounded-2xl p-0 w-full max-w-2xl overflow-hidden backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
            <div className="flex">
              <div className="hidden md:block w-1/2 h-64 md:h-auto">
                <img src={selectedPlace.image} alt={selectedPlace.name} className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">{selectedPlace.name}</h3>
                    <p className="text-sm text-slate-600 dark:text-white/70">{selectedPlace.description}</p>
                  </div>
                  <button onClick={() => setSelectedPlace(null)} className="p-2 rounded-lg hover:bg-white/25 transition-colors">
                    <X className="w-5 h-5 text-slate-700 dark:text-white" />
                  </button>
                </div>
                <div className="space-y-3">
                  <button onClick={() => { handleTravelWithSomeone(selectedPlace); setSelectedPlace(null); }} className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-700 hover:bg-white/35 transition-colors backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35">
                    Путешествовать с кем-то
                  </button>
                  <button onClick={() => { handleStartJourneyFromPlace(selectedPlace); setSelectedPlace(null); }} className="w-full px-4 py-3 rounded-xl bg-orange-500 border border-orange-600 hover:bg-orange-600 text-white font-semibold transition-colors">
                    Начать моё путешествие
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Post Modal */}
      {showCreatePost && (
        <CreatePostModal 
          onClose={() => setShowCreatePost(false)} 
          onSubmit={handleCreatePost}
        />
      )}

      {/* Profile Modal */}
      {showProfile && (
        <ProfileModal 
          user={currentUser}
          onClose={() => setShowProfile(false)}
        />
      )}

      {/* Survey Modal */}
      {showSurvey && (
        <SurveyModal 
          questions={surveyQuestions}
          answers={surveyAnswers}
          onChange={(id: string, value: string) => setSurveyAnswers(prev => ({ ...prev, [id]: value }))}
          onSubmit={async () => {
            try {
              await api.survey.submit({
                favorite_category: surveyAnswers.favorite_category,
                activity_level: surveyAnswers.activity_level,
                budget_level: surveyAnswers.budget_level,
                city: surveyAnswers.city,
              });
              setShowSurvey(false);
              // reload recs targeting city
              try {
                const recPosts = await api.recs.list();
                if (Array.isArray(recPosts) && recPosts.length > 0) {
                  setPosts(recPosts as any);
                }
              } catch {}
            } catch (e) {
              // keep modal open
            }
          }}
          onClose={() => setShowSurvey(false)}
        />
      )}

      {/* Map Modal */}
      <MapModal 
        points={mapPoints}
        isOpen={showMapModal}
        onClose={() => setShowMapModal(false)}
        title="Маршрут на карте"
      />
    </div>
    </div>
  );
}

function AuthForm({ onAuth }: { onAuth: (credentials: any) => void }) {
  const [mode, setMode] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAuth({ ...formData, mode });
  };

  return (
                <div className="rounded-3xl p-8 border shadow-2xl bg-white/25 border-gray-200/25 text-slate-900 backdrop-blur-sm dark:backdrop-blur-md dark:bg-black/25 dark:border-black/25 dark:text-white">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-2 dark:text-white">
          {mode === 'login' ? 'Добро пожаловать' : 'Создать аккаунт'}
        </h2>
        <p className="text-slate-600 dark:text-white/70">
          {mode === 'login' ? 'Войдите, чтобы продолжить' : 'Присоединяйтесь к сообществу'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === 'register' && (
          <div>
            <input
              type="text"
              placeholder="Ваше имя"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
            />
          </div>
        )}

        <div>
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors dark:backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
          />
        </div>

        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Пароль"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors pr-12 backdrop-blur-sm dark:backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 hover:text-white/80"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {mode === 'register' && (
          <div>
            <input
              type="password"
              placeholder="Подтвердите пароль"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
            />
          </div>
        )}

        <button 
          type="submit"
          className="w-full bg-orange-500 border border-orange-600 hover:bg-orange-600 text-white font-semibold px-4 py-3 rounded-xl shadow-lg transition-colors"
        >
          {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <button
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="text-slate-600 hover:text-slate-800 transition-all dark:text-white/70 dark:hover:text-white"
        >
          {mode === 'login' ? 'Нет аккаунта? Создать' : 'Уже есть аккаунт? Войти'}
        </button>
      </div>
    </div>
  );
}

function AdventureCard({ post, onLike, onComment, onMapClick }: { post: any, onLike: (id: any) => void, onComment: (id: any, text: string) => void, onMapClick?: (points: any[]) => void }) {
  const [comment, setComment] = useState('');
  const [showAllPhotos, setShowAllPhotos] = useState(false);

  return (
    <article className="backdrop-blur-md bg-white/25 border border-gray-200/25 p-4 rounded-2xl text-slate-900 shadow-xl dark:bg-black/25 dark:border-black/25 dark:text-white">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center font-bold text-white text-sm">
          {post.author[0]}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-lg text-slate-900 dark:text-white">{post.title}</h3>
              <div className="text-xs text-slate-600 dark:text-white/60">{post.author} • {formatDate(post.id)}</div>
            </div>
            <button className="p-1 rounded-full hover:bg-gray-100 transition-all dark:hover:bg-black/25">
              <Share2 className="w-4 h-4 text-white/60" />
            </button>
          </div>
        </div>
      </div>

      <p className="text-slate-800 mb-3 leading-relaxed text-sm dark:text-white/90">{post.description}</p>

      {/* Photo Gallery */}
      {post.photos && post.photos.length > 0 && (
        <div className="mb-4">
          <div className="grid grid-cols-3 gap-1 rounded-xl overflow-hidden">
            {(showAllPhotos ? post.photos : post.photos.slice(0, 4)).map((photo: any, index: number) => (
              <div 
                key={index} 
                className={`relative aspect-square overflow-hidden ${
                  index === 3 && !showAllPhotos && post.photos.length > 4 ? 'cursor-pointer' : ''
                }`}
                onClick={() => {
                  if (index === 3 && !showAllPhotos && post.photos.length > 4) {
                    setShowAllPhotos(true);
                  }
                }}
              >
                {photo.url ? (
                  <img 
                    src={photo.url} 
                    alt={`Photo ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
                      <Camera className="w-8 h-8 text-white/80" />
                    </div>
                )}
                {index === 3 && !showAllPhotos && post.photos.length > 4 && (
                  <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                    <div className="text-white text-lg font-bold">+{post.photos.length - 4}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Route Map */}
      {post.route && post.route.length > 0 && (
        <div className="mb-4 rounded-xl overflow-hidden border border-gray-200 dark:border-black/25">
          <MapComponent 
            points={post.route.map((point: any, index: number) => ({
              id: index,
              name: point.name || `Точка ${index + 1}`,
              lat: point.lat,
              lng: point.lng,
              description: point.description
            }))}
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between mb-3 pb-3 border-b border-gray-200 dark:border-black/25">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onLike(post.id)} 
            className={`flex items-center gap-1 px-3 py-1 rounded-full transition-all text-sm ${
              post.liked ? 'bg-red-500/25 text-red-300' : 'bg-white/25 text-slate-700 hover:bg-white/35 dark:bg-black/25 dark:text-white/80 dark:hover:bg-black/35'
            } backdrop-blur-sm`}
          >
            <Heart className={`w-4 h-4 ${post.liked ? 'fill-current' : ''}`} />
            {post.likes}
          </button>
          <button className="flex items-center gap-1 px-3 py-1 rounded-full bg-white/25 text-slate-700 hover:bg-white/35 transition-all text-sm backdrop-blur-sm dark:bg-black/25 dark:text-white/80 dark:hover:bg-black/35">
            <MessageCircle className="w-4 h-4" />
            {post.comments.length}
          </button>
        </div>
        <div className="flex items-center gap-1 text-slate-600 text-xs dark:text-white/70">
          <MapPin className="w-3 h-3" />
          {post.route?.length || 0} точек
          {post.route && post.route.length > 0 && (
            <button 
              onClick={() => {
                if (onMapClick) {
                  onMapClick(post.route.map((point: any, index: number) => ({
                    id: index,
                    name: point.name || `Точка ${index + 1}`,
                    lat: point.lat,
                    lng: point.lng,
                    description: point.description
                  })));
                }
              }}
              className="ml-2 text-orange-500 hover:text-orange-600 text-xs underline"
            >
              Открыть карту
            </button>
          )}
        </div>
      </div>

      {/* Comments */}
      <div className="space-y-2">
        {post.comments.map((c: any) => (
          <div key={c.id} className="flex items-start gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
              {c.author[0]}
            </div>
            <div className="flex-1 bg-white/25 border border-gray-200/25 rounded-xl px-3 py-2 text-slate-900 backdrop-blur-sm dark:backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white">
              <div className="font-semibold text-slate-900 text-xs mb-1 dark:text-white">{c.author}</div>
              <div className="text-slate-800 text-xs dark:text-white/90">{c.text}</div>
            </div>
          </div>
        ))}

        <div className="flex gap-2 mt-3">
          <input 
            value={comment} 
            onChange={(e)=>setComment(e.target.value)} 
            placeholder="Оставить комментарий" 
            className="flex-1 rounded-xl px-3 py-2 bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors text-sm backdrop-blur-sm dark:backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white" 
          />
          <button 
            onClick={() => { onComment(post.id, comment); setComment(''); }} 
            className="bg-orange-500 border border-orange-600 px-4 py-2 rounded-xl text-white font-semibold hover:bg-orange-600 transition-colors text-sm"
          >
            Отправить
          </button>
        </div>
      </div>
    </article>
  );
}


function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-800"></div>
      
      {/* Animated gradient orbs */}
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-orange-400/30 to-pink-400/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-gradient-to-r from-blue-400/20 to-purple-400/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-r from-green-400/20 to-blue-400/30 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-1/3 right-1/3 w-64 h-64 bg-gradient-to-r from-yellow-400/25 to-orange-400/35 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>
      
      {/* Floating particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-black/25 rounded-full animate-ping"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>
    </div>
  );
}

function SeaLoading() {
  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <AnimatedBackground />
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-8">
            <svg width="240" height="100" viewBox="0 0 240 100" className="mx-auto">
              <defs>
                <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#FB923C" />
                  <stop offset="50%" stopColor="#F59E0B" />
                  <stop offset="100%" stopColor="#EF4444" />
                </linearGradient>
              </defs>
              <path 
                d="M0 50 Q60 20 120 50 T240 50" 
                stroke="url(#waveGradient)" 
                strokeWidth="6" 
                strokeLinecap="round" 
                fill="none"
              >
                <animate 
                  attributeName="d" 
                  dur="3s" 
                  repeatCount="indefinite" 
                  values="M0 50 Q60 20 120 50 T240 50; M0 50 Q60 80 120 50 T240 50; M0 50 Q60 20 120 50 T240 50" 
                />
              </path>
            </svg>
          </div>
          <div className="text-3xl font-bold text-white mb-4">Готовим приключение...</div>
          <div className="text-lg text-white/70">Пока мы собираем идеи, представь море и лёгкий бриз</div>
        </div>
      </div>
    </div>
  );
}

// ----------------- Mock data & helpers -----------------

// function _mockPosts() {
//   return [
//     {
//       id: Date.now() - 1000*60*60*24*7,
//       title: 'Вечер у причала и джаз',
//       author: 'Ольга',
//       route: sampleRoute(),
//       photos: [
//         { gradient: 'from-blue-500 to-cyan-400', location: 'Набережная' },
//         { gradient: 'from-orange-500 to-yellow-400', location: 'Кофейня' },
//         { gradient: 'from-purple-500 to-pink-400', location: 'Джаз-клуб' },
//       ],
//       likes: 12,
//       liked: false,
//       comments: [{id:1,author:'Пётр',text:'Было нереально!'}],
//       description: 'Небольшая прогулка вдоль набережной, остановка в кофейне и джаз на вечере. Отличные фото у моста и невероятная атмосфера в клубе. Рекомендую всем любителям спокойных вечеров с хорошей музыкой.',
//     },
//     {
//       id: Date.now() - 1000*60*60*24*2,
//       title: 'Книжный квест в старом подвальчике',
//       author: 'Иван',
//       route: sampleRoute(4),
//       photos: [
//         { gradient: 'from-amber-500 to-orange-400', location: 'Антикварная лавка' },
//         { gradient: 'from-green-500 to-emerald-400', location: 'Букинистический магазин' },
//         { gradient: 'from-red-500 to-rose-400', location: 'Уютная кофейня' },
//         { gradient: 'from-indigo-500 to-purple-400', location: 'Библиотека' },
//         { gradient: 'from-teal-500 to-cyan-400', location: 'Книжный клуб' },
//       ],
//       likes: 7,
//       liked: false,
//       comments: [{id:2,author:'Мария',text:'Нашли редкую книгу :)'}],
//       description: 'Искали редкие томы в старых лавках и закончили в уютной кофейне. Удивительное путешествие по книжным местам города с находками и открытиями.',
//     },
//     {
//       id: Date.now() - 1000*60*60*24*1,
//       title: 'Фотосессия на рассвете у моря',
//       author: 'Анна',
//       route: sampleRoute(3),
//       photos: [
//         { gradient: 'from-pink-400 to-rose-300', location: 'Пляж' },
//         { gradient: 'from-orange-400 to-amber-300', location: 'Скалы' },
//         { gradient: 'from-blue-400 to-cyan-300', location: 'Маяк' },
//       ],
//       likes: 24,
//       liked: true,
//       comments: [
//         {id:3,author:'Дима',text:'Какие краски! 🌅'},
//         {id:4,author:'Лена',text:'Хочу тоже так!'}
//       ],
//       description: 'Встали в 5 утра ради этих кадров! Золотой час у моря, розовые облака и невероятные отражения в воде. Каждая минута стоила раннего подъема.',
//     }
//   ];
// }

// function _mockPhotos() {
//   return [
//     { gradient: 'from-blue-500 to-cyan-400', location: 'Парк' },
//     { gradient: 'from-green-500 to-emerald-400', location: 'Кафе' },
//     { gradient: 'from-purple-500 to-pink-400', location: 'Музей' },
//     { gradient: 'from-orange-500 to-yellow-400', location: 'Мост' },
//     { gradient: 'from-red-500 to-rose-400', location: 'Площадь' },
//   ];
// }

// mockGroups removed: replaced by live chats UI in 'groups' tab

function sampleRoute(n=3) {
  return Array.from({length:n}).map((_,i)=>({
    lat:55.7558 + (Math.random() - 0.5) * 0.02, 
    lng:37.6173 + (Math.random() - 0.5) * 0.02, 
    name:`Точка ${i+1}`,
    description: `Описание точки ${i+1}`
  }));
}

function formatDate(ts: number) {
  const d = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) return 'Сегодня';
  if (days === 1) return 'Вчера';
  if (days < 7) return `${days} дня назад`;
  return d.toLocaleDateString('ru-RU');
}

function CreatePostModal({ onClose, onSubmit }: { onClose: () => void, onSubmit: (data: any) => void }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    photos: [] as string[]
  });
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${(import.meta as any).env?.VITE_API_URL || "http://localhost:8000"}/posts/upload-photo`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          setFormData(prev => ({
            ...prev,
            photos: [...prev.photos, result.url]
          }));
        }
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white/25 border border-gray-200/25 rounded-2xl p-6 w-full max-w-md backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">Создать приключение</h3>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/25 transition-colors"
          >
            <X className="w-5 h-5 text-slate-700 dark:text-white" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="text"
              placeholder="Название приключения"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
            required
          />
        </div>

        <div>
          <textarea
              placeholder="Описание приключения"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 placeholder:text-slate-500 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white resize-none"
              rows={4}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-white mb-2">
            Фотографии
          </label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileUpload}
              className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-500 file:text-white hover:file:bg-orange-600 transition-colors backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
              disabled={uploading}
            />
            {uploading && (
              <p className="text-sm text-slate-600 dark:text-white/70 mt-2">Загружаем фото...</p>
            )}
            {formData.photos.length > 0 && (
              <div className="mt-2">
                <p className="text-sm text-slate-600 dark:text-white/70 mb-2">
                  Загружено фото: {formData.photos.length}
                </p>
              <div className="grid grid-cols-3 gap-2">
                  {formData.photos.map((photo, index) => (
                    <div key={index} className="relative">
                      <img 
                        src={photo} 
                        alt={`Photo ${index + 1}`}
                        className="w-full h-20 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                        onClick={() => setFormData(prev => ({
                          ...prev,
                          photos: prev.photos.filter((_, i) => i !== index)
                        }))}
                        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 transition-colors"
                    >
                      ×
                    </button>
                  </div>
                ))}
                </div>
              </div>
            )}
        </div>

          <div className="flex gap-3">
          <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-700 hover:bg-white/35 transition-colors backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35"
            >
              Отмена
          </button>
          <button
              type="submit"
              className="flex-1 px-4 py-3 rounded-xl bg-orange-500 border border-orange-600 hover:bg-orange-600 text-white font-semibold transition-colors"
            >
              Создать
          </button>
        </div>
      </form>
      </div>
    </div>
  );
}

function ProfileModal({ user, onClose }: { user: any, onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white/25 border border-gray-200/25 rounded-2xl p-6 w-full max-w-md backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">Мой профиль</h3>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/25 transition-colors"
          >
            <X className="w-5 h-5 text-slate-700 dark:text-white" />
          </button>
        </div>
        
        <div className="text-center">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center font-bold text-white text-2xl mx-auto mb-4">
            {user?.username?.[0] || 'U'}
          </div>
          <h4 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {user?.username || 'Пользователь'}
          </h4>
          <p className="text-slate-600 dark:text-white/70 mb-4">
            {user?.email || 'email@example.com'}
          </p>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-white/25 border border-gray-200/25 rounded-xl p-4 backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
              <div className="text-2xl font-bold text-orange-500 dark:text-orange-300">
                {user?.posts_count || 0}
              </div>
              <div className="text-sm text-slate-600 dark:text-white/70">
                Приключений
              </div>
            </div>
            <div className="bg-white/25 border border-gray-200/25 rounded-xl p-4 backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
              <div className="text-2xl font-bold text-orange-500 dark:text-orange-300">
                {user?.likes_count || 0}
              </div>
              <div className="text-sm text-slate-600 dark:text-white/70">
                Лайков получено
              </div>
            </div>
          </div>
          
          <div className="bg-white/25 border border-gray-200/25 rounded-xl p-4 backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
            <h5 className="font-semibold text-slate-900 dark:text-white mb-2">О себе</h5>
            <p className="text-sm text-slate-600 dark:text-white/70">
              Люблю путешествовать и открывать новые места. 
              Создаю воспоминания через приключения и делюсь ими с миром.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function SurveyModal({ questions, answers, onChange, onSubmit, onClose }: { questions: any[], answers: Record<string,string>, onChange: (id: string, value: string)=>void, onSubmit: ()=>void, onClose: ()=>void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white/25 border border-gray-200/25 rounded-2xl p-6 w-full max-w-md backdrop-blur-sm dark:bg-black/25 dark:border-black/25">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">Короткий опрос</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/25 transition-colors">
            <X className="w-5 h-5 text-slate-700 dark:text-white" />
          </button>
        </div>
        <div className="space-y-4">
          {questions.map((q:any)=> (
            <div key={q.id}>
              <label className="block text-sm font-medium text-slate-900 dark:text-white mb-2">{q.label}</label>
              {q.type === 'select' ? (
                <select
                  value={answers[q.id] || ''}
                  onChange={(e)=> onChange(q.id, e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                >
                  <option value="" disabled>Выберите...</option>
                  {(q.options||[]).map((opt:string)=> (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  value={answers[q.id] || ''}
                  onChange={(e)=> onChange(q.id, e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-900 outline-none focus:border-orange-400 transition-colors backdrop-blur-sm dark:bg-slate-900 dark:border-slate-700 dark:text-white"
                  placeholder={q.id==='city' ? 'Например: Saint Petersburg' : ''}
                />
              )}
            </div>
          ))}
        </div>
        <div className="mt-6 flex gap-3">
          <button onClick={onClose} className="flex-1 px-4 py-3 rounded-xl bg-white/25 border border-gray-200/25 text-slate-700 hover:bg-white/35 transition-colors backdrop-blur-sm dark:bg-black/25 dark:border-black/25 dark:text-white dark:hover:bg-black/35">Позже</button>
          <button onClick={onSubmit} className="flex-1 px-4 py-3 rounded-xl bg-orange-500 border border-orange-600 hover:bg-orange-600 text-white font-semibold transition-colors">Готово</button>
        </div>
      </div>
    </div>
  );
}