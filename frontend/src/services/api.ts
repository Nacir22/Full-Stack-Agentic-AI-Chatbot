// Client API isolé : toute communication avec le backend FastAPI passe par ici.
// L'URL de base vient de NEXT_PUBLIC_API_BASE_URL (voir .env.local.example).

import type {
  ChatResponse,
  Conversation,
  ConversationDetail,
  DocumentItem,
} from "@/lib/types";

const BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.detail ?? "";
    } catch {
      // corps non JSON : on garde le message générique
    }
    throw new Error(detail || `Erreur ${res.status} (${res.statusText})`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export const api = {
  sendChat(message: string, conversationId?: string): Promise<ChatResponse> {
    return fetch(`${BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId ?? null,
      }),
    }).then((r) => handle<ChatResponse>(r));
  },

  listConversations(): Promise<Conversation[]> {
    return fetch(`${BASE}/conversations`).then((r) =>
      handle<Conversation[]>(r),
    );
  },

  getConversation(id: string): Promise<ConversationDetail> {
    return fetch(`${BASE}/conversations/${id}`).then((r) =>
      handle<ConversationDetail>(r),
    );
  },

  uploadDocument(file: File): Promise<DocumentItem> {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${BASE}/upload`, { method: "POST", body: form }).then((r) =>
      handle<DocumentItem>(r),
    );
  },

  listDocuments(): Promise<DocumentItem[]> {
    return fetch(`${BASE}/documents`).then((r) => handle<DocumentItem[]>(r));
  },

  deleteDocument(id: string): Promise<void> {
    return fetch(`${BASE}/documents/${id}`, { method: "DELETE" }).then((r) =>
      handle<void>(r),
    );
  },
};
