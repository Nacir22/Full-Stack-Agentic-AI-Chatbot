"use client";

import { ChangeEvent, useRef } from "react";
import type { Conversation, DocumentItem } from "@/lib/types";

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  documents: DocumentItem[];
  onUpload: (file: File) => void;
  onDeleteDocument: (id: string) => void;
}

export function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  documents,
  onUpload,
  onDeleteDocument,
}: SidebarProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) onUpload(file);
    event.target.value = "";
  }

  return (
    <aside className="flex w-72 flex-col border-r bg-white">
      <div className="p-4">
        <button
          onClick={onNew}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + Nouvelle conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-2 py-1 text-xs font-semibold uppercase text-slate-400">
          Conversations
        </p>
        {conversations.length === 0 && (
          <p className="px-2 py-1 text-xs text-slate-400">Aucune pour l'instant.</p>
        )}
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`mb-1 block w-full truncate rounded-md px-2 py-2 text-left text-sm ${
              c.id === activeId
                ? "bg-blue-50 text-blue-700"
                : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            {c.title ?? `Conversation ${c.id.slice(0, 8)}`}
          </button>
        ))}
      </div>

      <div className="border-t p-3">
        <p className="mb-2 text-xs font-semibold uppercase text-slate-400">
          Documents (RAG)
        </p>
        <button
          onClick={() => fileRef.current?.click()}
          className="mb-2 w-full rounded-lg border border-dashed border-slate-300 px-3 py-2 text-sm text-slate-600 hover:border-blue-400 hover:text-blue-600"
        >
          + Uploader un document
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.md,.pdf"
          className="hidden"
          onChange={handleFile}
        />
        <ul className="max-h-40 space-y-1 overflow-y-auto">
          {documents.map((d) => (
            <li
              key={d.id}
              className="flex items-center justify-between rounded-md px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              <span className="truncate" title={d.filename}>
                {d.filename}{" "}
                <span className="text-slate-400">({d.num_chunks})</span>
              </span>
              <button
                onClick={() => onDeleteDocument(d.id)}
                className="ml-2 text-slate-400 hover:text-red-600"
                aria-label="Supprimer"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
