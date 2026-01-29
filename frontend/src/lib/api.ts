// API client for OPAL Orchestrator

import type {
  ChatRequest,
  ChatResponse,
  Capability,
  CapabilitySearchResult,
  ConversationDetail,
  ConversationSummary,
  Lab,
  SourceDocument,
} from '@/types';

/**
 * Get the API URL at runtime from config file.
 * This allows the API URL to be configured via environment variables
 * in Rancher2 ConfigMaps without rebuilding the image.
 */
let API_URL: string;

async function initializeAPIUrl(): Promise<string> {
  try {
    // Try to load from runtime config file first
    const response = await fetch('/config.json');
    if (response.ok) {
      const config = await response.json();
      return config.apiUrl || '/api';
    }
  } catch {
    // Fall back if config file doesn't exist
    console.error("Error loading config.json, using default API URL");
  }
  return process.env.NEXT_PUBLIC_API_URL || '/api';
}

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  if (API_URL == undefined) {
    API_URL = await initializeAPIUrl();
  }

  const url = `${API_URL}${endpoint}`;
  console.log('requesting: ', endpoint, options);
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || `API error: ${response.status}`,
      response.status,
      error
    );
  }

  return response.json();
}

// Chat API
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return fetchAPI<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// Capabilities API
export async function searchCapabilities(
  query: string,
  options: {
    lab?: string;
    modality?: string;
    tags?: string[];
    top_k?: number;
  } = {}
): Promise<CapabilitySearchResult[]> {
  const params = new URLSearchParams({ q: query });

  if (options.lab) params.append('lab', options.lab);
  if (options.modality) params.append('modality', options.modality);
  if (options.tags) {
    options.tags.forEach((tag) => params.append('tags', tag));
  }
  if (options.top_k) params.append('top_k', options.top_k.toString());

  return fetchAPI<CapabilitySearchResult[]>(`/capabilities/search?${params}`);
}

// Labs API
export async function getLabs(): Promise<Lab[]> {
  return fetchAPI<Lab[]>('/labs');
}

// Capabilities API - list all
export async function getCapabilities(): Promise<Capability[]> {
  return fetchAPI<Capability[]>('/capabilities');
}

// Sources API
export async function getSources(): Promise<SourceDocument[]> {
  return fetchAPI<SourceDocument[]>('/sources');
}

export async function getSourceChunks(sourceId: string): Promise<unknown[]> {
  return fetchAPI<unknown[]>(`/sources/${sourceId}/chunks`);
}

// Health check
export async function healthCheck(): Promise<{ status: string }> {
  return fetchAPI<{ status: string }>('/health');
}

// Ingest PDF (FormData)
export async function ingestPDF(
  file: File,
  title: string,
  description?: string
): Promise<{ source_document_id: string; chunks_created: number; message: string }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  if (description) {
    formData.append('description', description);
  }

  const response = await fetch(`${API_URL}/ingest/pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || `API error: ${response.status}`,
      response.status,
      error
    );
  }

  return response.json();
}

// Ingest URL
export async function ingestURL(
  url: string,
  title: string,
  description?: string
): Promise<{ source_document_id: string; chunks_created: number; message: string }> {
  return fetchAPI('/ingest/url', {
    method: 'POST',
    body: JSON.stringify({ url, title, description }),
  });
}

// Conversations API
export async function getConversations(
  skip: number = 0,
  limit: number = 50
): Promise<ConversationSummary[]> {
  return fetchAPI<ConversationSummary[]>(`/conversations?skip=${skip}&limit=${limit}`);
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  return fetchAPI<ConversationDetail>(`/conversations/${id}`);
}

export async function updateConversation(
  id: string,
  update: { title?: string }
): Promise<ConversationDetail> {
  return fetchAPI<ConversationDetail>(`/conversations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(update),
  });
}

export async function deleteConversation(id: string): Promise<{ message: string; id: string }> {
  return fetchAPI<{ message: string; id: string }>(`/conversations/${id}`, {
    method: 'DELETE',
  });
}
