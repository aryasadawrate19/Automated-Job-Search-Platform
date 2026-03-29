// Shared TypeScript types — mirrors backend Pydantic schemas

export type ExperienceLevel = 'junior' | 'mid' | 'senior' | 'lead';
export type RemotePreference = 'only' | 'preferred' | 'open';
export type AIProvider = 'anthropic' | 'gemini' | 'openai';

export interface Job {
  id: string;
  source: string;
  source_url: string;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  description_raw: string;
  description_normalized: string;
  skills_extracted: string[];
  experience_level: ExperienceLevel;
  salary_min: number | null;
  salary_max: number | null;
  posted_at: string;
  ingested_at: string;
}

export interface User {
  id: string;
  email: string;
  skills: string[];
  experience_years: number;
  experience_level: ExperienceLevel;
  preferred_roles: string[];
  preferred_locations: string[];
  remote_preference: RemotePreference;
  ai_provider: AIProvider;
  has_anthropic_key: boolean;
  has_gemini_key: boolean;
  has_openai_key: boolean;
  created_at: string;
  updated_at: string;
}

export interface MatchExplanation {
  matched_skills: string[];
  missing_skills: string[];
  experience_alignment: string;
  location_note: string;
  relevance_summary: string;
  improvement_tips: string[];
}

export interface Match {
  id: string;
  user_id: string;
  job_id: string;
  rule_score: number;
  semantic_score: number;
  final_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
  computed_at: string;
  job?: Job;
  explanation_detail?: MatchExplanation;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export enum AiProviderEnum {
  ANTHROPIC = 'anthropic',
  GEMINI = 'gemini',
  OPENAI = 'openai'
}

export interface ApiKeyRequest {
  api_key: string;
}

export interface AiProviderRequest {
  ai_provider: AiProviderEnum;
}

// Aliases used by frontend
export type UserProfile = User;
export type MatchResponse = Match;
export type MatchListResponse = PaginatedResponse<Match>;
