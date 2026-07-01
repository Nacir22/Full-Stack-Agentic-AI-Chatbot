"use client";

import { FormEvent, useState } from "react";

export function Composer({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  }

  return (
    <form onSubmit={submit} className="flex gap-2 border-t bg-white px-6 py-4">
      <input
        className="flex-1 rounded-full border border-slate-300 px-4 py-2 text-sm outline-none focus:border-blue-500"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Écris ton message…"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-full bg-blue-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-50"
      >
        Envoyer
      </button>
    </form>
  );
}
