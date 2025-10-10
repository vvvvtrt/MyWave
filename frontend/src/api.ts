const BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export type Comment = { id: number; post_id: number; text: string; author: string };
export type RoutePoint = { lat: number; lng: number };
export type Post = {
  id: number;
  title: string;
  author: string;
  description?: string;
  likes: number;
  liked: boolean;
  comments: Comment[];
  route: RoutePoint[];
  photos: string[] | any[];
};

async function http<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { ...headers, ...(options?.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  health: () => http<{ status: string }>(`/health`),
  login: (payload: { email?: string; password?: string }) =>
    http<{ access_token: string; token_type: string }>(`/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: payload.email || '',
        password: payload.password || ''
      }).toString(),
    }),
  register: (payload: { email?: string; password?: string; username?: string; full_name?: string }) =>
    http<{ access_token: string; token_type: string }>(`/auth/register`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getCurrentUser: () => http<{ id: number; username: string; email: string; full_name?: string; posts_count: number; likes_count: number }>(`/auth/me`),
  posts: {
    list: () => http<Post[]>(`/posts/`),
    get: (id: number) => http<Post>(`/posts/${id}`),
    create: (payload: { title: string; description?: string; photos?: string[] }) =>
      http<Post>(`/posts/`, { method: "POST", body: JSON.stringify(payload) }),
    like: (id: number) => http<Post>(`/posts/${id}/like`, { method: "POST" }),
  },
  comments: {
    listByPost: (postId: number) => http<Comment[]>(`/comments/by-post/${postId}`),
    add: (payload: { post_id: number; text: string }) =>
      http<Comment>(`/comments/`, { method: "POST", body: JSON.stringify(payload) }),
  },
  groups: {
    list: () => http<Array<{ id: number; name: string }>>(`/groups/`),
    create: (name: string) => http<{ id: number; name: string }>(`/groups/`, { method: 'POST', body: JSON.stringify({ name }) }),
    addMember: (groupId: number, userId: number) => http<{ status: string }>(`/groups/${groupId}/add-member`, { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  },
  places: {
    list: () => http<Array<{ id: number; name: string; image: string; description: string }>>(`/places/`),
  },
  chats: {
    list: () => http<Array<{ id: number; name: string; last_message?: { text: string; created_at?: string } }>>(`/chats/`),
    messages: (chatId: number) => http<Array<{ id: number; text: string; author: string; created_at?: string }>>(`/chats/${chatId}/messages`),
    send: (chatId: number, text: string) => http<{ id: number; text: string; author: string; created_at?: string }>(`/chats/${chatId}/messages`, { method: 'POST', body: JSON.stringify({ text }) }),
    create: (name: string) => http<{ id: number; name: string }>(`/chats/`, { method: 'POST', body: JSON.stringify({ name }) }),
    createDM: (username: string) => http<{ id: number; name: string }>(`/chats/dm`, { method: 'POST', body: JSON.stringify({ username }) }),
  },
  search: (q: string) => http<Post[]>(`/search/?q=${encodeURIComponent(q)}`),
  survey: {
    status: () => http<{ completed: boolean }>(`/survey/status`),
    questions: () => http<{ questions: Array<{ id: string; label: string; type: string; options?: string[] }> }>(`/survey/questions`),
    submit: (payload: { favorite_category?: string; activity_level?: string; budget_level?: string; city?: string }) =>
      http<{ status: string }>(`/survey/`, { method: 'POST', body: JSON.stringify(payload) }),
  },
  recs: {
    list: () => http<Post[]>(`/recs/`),
  }
};





