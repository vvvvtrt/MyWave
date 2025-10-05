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
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  health: () => http<{ status: string }>(`/health`),
  login: (payload: { email?: string; password?: string; name?: string }) =>
    http<{ token: string; user: { id: number; name: string; email: string } }>(`/auth/login`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  posts: {
    list: () => http<Post[]>(`/posts/`),
    get: (id: number) => http<Post>(`/posts/${id}`),
    create: (payload: { title: string; description?: string }) =>
      http<Post>(`/posts/`, { method: "POST", body: JSON.stringify(payload) }),
    like: (id: number) => http<Post>(`/posts/${id}/like`, { method: "POST" }),
  },
  comments: {
    listByPost: (postId: number) => http<Comment[]>(`/comments/by-post/${postId}`),
    add: (payload: { post_id: number; text: string }) =>
      http<Comment>(`/comments/`, { method: "POST", body: JSON.stringify(payload) }),
  },
  groups: {
    list: () => http<Array<{ id: number; name: string; members: any[] }>>(`/groups/`),
  },
  search: (q: string) => http<Post[]>(`/search/?q=${encodeURIComponent(q)}`),
};





