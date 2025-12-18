// API Types for OPAL Orchestrator

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, unknown>;
}

export interface Citation {
  source_document_id: string;
  chunk_id?: string;
  quote: string;
  source_title?: string;
}

export interface PlanStep {
  step_id: string;
  objective: string;
  recommended_facility: string;
  capability_ids: string[];
  inputs: string[];
  outputs: string[];
  constraints: string[];
  dependencies: string[];
  decision_points: string[];
  citations: Citation[];
  is_hypothesis: boolean;
}

export interface RiskItem {
  risk: string;
  impact: string;
  alternative?: string;
}

export interface OPALPlan {
  goal_summary: string;
  assumptions: string[];
  steps: PlanStep[];
  open_questions: string[];
  risks_and_alternatives: RiskItem[];
  created_at?: string;
}

export interface SearchResult {
  chunk_id: string;
  source_document_id: string;
  source_title: string;
  text: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  plan?: OPALPlan;
  sources: SearchResult[];
}

export interface Capability {
  id: string;
  facility_id: string;
  name: string;
  description?: string;
  modalities?: string[];
  throughput?: string;
  sample_requirements?: Record<string, unknown>;
  constraints?: Record<string, unknown>;
  typical_outputs?: string[];
  readiness_level?: string;
  tags?: string[];
  facility_name: string;
  lab_name: string;
  lab_institution: string;
}

export interface CapabilitySearchResult {
  capability: Capability;
  relevance_score: number;
  source_chunks: SearchResult[];
}

export interface Lab {
  id: string;
  name: string;
  institution: string;
  location?: string;
  description?: string;
  urls?: Record<string, string>;
  contacts?: Record<string, string>;
}

export interface Facility {
  id: string;
  lab_id: string;
  name: string;
  description?: string;
}

export interface SourceDocument {
  id: string;
  type: string;
  title: string;
  url_or_path: string;
  ingested_at: string;
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  preview: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string | null;
  messages: ChatMessage[];
  plan: OPALPlan | null;
  sources: SearchResult[];
  created_at: string;
  updated_at: string;
}
