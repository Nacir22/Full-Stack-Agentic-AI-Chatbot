"use client";

// Composant principal : orchestre l'état (conversations, messages, documents),
// gère le chargement et les erreurs, et relie l'UI au service API.

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/services/api";
import type { Conversation, DocumentItem, Message } from "@/lib/types";
import { MessageBubble } from "@/components/MessageBubble";
import { Composer } from "@/components/Composer";
import { Sidebar } from "@/components/Sidebar";

export function ChatApp() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const refreshConversations = useCallback(async () => {
    try {
      setConversations(await api.listConversations());
    } catch {
      /* silencieux : la liste peut rester vide */
    }
  }, []);

  const refreshDocuments = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments());
    } catch {
      /* silencieux */
    }
  }, []);

  useEffect(() => {
    refreshConversations();
    refreshDocuments();
  }, [refreshConversations, refreshDocuments]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const selectConversation = useCallback(async (id: string) => {
    setError(null);
    try {
      const detail = await api.getConversation(id);
      setActiveId(id);
      setMessages(detail.messages);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  function newConversation() {
    setActiveId(null);
    setMessages([]);
    setError(null);
  }

  async function send(text: string) {
    setError(null);
    const optimistic: Message = {
      id: `tmp-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((m) => [...m, optimistic]);
    setLoading(true);
    try {
      const res = await api.sendChat(text, activeId ?? undefined);
      const assistant: Message = {
        id: res.message_id,
        role: "assistant",
        content: res.response,
        created_at: new Date().toISOString(),
      };
      setMessages((m) => [...m, assistant]);
      if (!activeId) {
        setActiveId(res.conversation_id);
        refreshConversations();
      }
    } catch (e) {
      setError((e as Error).message);
      setMessages((m) => m.filter((x) => x.id !== optimistic.id));
    } finally {
      setLoading(false);
    }
  }

  async function upload(file: File) {
    setError(null);
    try {
      await api.uploadDocument(file);
      refreshDocuments();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function removeDocument(id: string) {
    try {
      await api.deleteDocument(id);
      refreshDocuments();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="flex h-screen">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={newConversation}
        documents={documents}
        onUpload={upload}
        onDeleteDocument={removeDocument}
      />

      <main className="flex flex-1 flex-col">
        <header className="border-b bg-white px-6 py-4">
          <h1 className="text-lg font-semibold">Agentic AI Chatbot</h1>
          <p className="text-xs text-slate-500">LangGraph · RAG · FastAPI</p>
        </header>

        <div className="flex-1 space-y-3 overflow-y-auto px-6 py-4">
          {messages.length === 0 && !loading && (
            <p className="mt-10 text-center text-sm text-slate-400">
              Pose une question pour démarrer la conversation.
            </p>
          )}
          {messages.map((m) => (
            <MessageBubble key={m.id} role={m.role} content={m.content} />
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-400">
                L'agent réfléchit…
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {error && (
          <div className="mx-6 mb-2 rounded-md bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <Composer disabled={loading} onSend={send} />
      </main>
    </div>
  );
}
