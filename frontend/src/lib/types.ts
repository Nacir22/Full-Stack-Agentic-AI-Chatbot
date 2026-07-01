// Types partagés avec l'API backend (schémas Pydantic côté FastAPI).

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  response: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  content_type: string | null;
  size_bytes: number;
  num_chunks: number;
  status: string;
  created_at: string;
}
