/**
 * API client utilities for communicating with the OmniDoc backend.
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Types
export interface DocumentTemplate {
  id: string;
  name: string;
  category?: string;
  description?: string;
  prompt_key?: string;
  agent_class?: string;
  dependencies: string[];
  priority?: string;
  owner?: string;
  status?: string;
  audience?: string;
  stage?: {
    label?: string;
    notes?: string;
  };
  must_have?: string;
  usage_frequency?: string;
  notes?: string;
}

export interface DocumentCatalogResponse {
  generated_at?: string;
  source?: string;
  documents: DocumentTemplate[];
}

export interface ProjectCreateRequest {
  user_idea: string;
  selected_documents: string[];
  provider_name?: string;
  codebase_path?: string;
}

export interface ProjectCreateResponse {
  project_id: string;
  status: string;
  message?: string;
}

export interface ProjectStatusResponse {
  project_id: string;
  status: string;
  selected_documents: string[];
  completed_documents: string[];
  error?: string;
  updated_at?: string;
}

export interface GeneratedDocument {
  id: string;
  name: string;
  status: string;
  file_path?: string;
  content?: string;
}

export interface ProjectDocumentsResponse {
  project_id: string;
  documents: GeneratedDocument[];
}

// API functions
export async function fetchJSON<T>(url: string): Promise<T> {
  try {
    const response = await apiClient.get<T>(url);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.status} ${error.response.statusText}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error(`Network Error: Unable to connect to backend at ${API_BASE_URL}. Is the server running?`);
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
}

export async function postJSON<T>(url: string, data: unknown): Promise<T> {
  try {
    const response = await apiClient.post<T>(url, data);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error status
      const errorMsg = error.response.data?.detail || error.response.statusText;
      throw new Error(`API Error: ${error.response.status} - ${errorMsg}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error(`Network Error: Unable to connect to backend at ${API_BASE_URL}. Is the server running?`);
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
}

// Document templates
export async function getDocumentTemplates(): Promise<DocumentCatalogResponse> {
  return fetchJSON<DocumentCatalogResponse>('/api/document-templates');
}

// Projects
export async function createProject(
  request: ProjectCreateRequest
): Promise<ProjectCreateResponse> {
  return postJSON<ProjectCreateResponse>('/api/projects', request);
}

export async function getProjectStatus(
  projectId: string
): Promise<ProjectStatusResponse> {
  return fetchJSON<ProjectStatusResponse>(`/api/projects/${projectId}/status`);
}

export async function getProjectDocuments(
  projectId: string
): Promise<ProjectDocumentsResponse> {
  return fetchJSON<ProjectDocumentsResponse>(
    `/api/projects/${projectId}/documents`
  );
}

export async function getDocument(
  projectId: string,
  documentId: string
): Promise<GeneratedDocument> {
  return fetchJSON<GeneratedDocument>(
    `/api/projects/${projectId}/documents/${documentId}`
  );
}

export function getDocumentDownloadUrl(
  projectId: string,
  documentId: string
): string {
  return `${API_BASE_URL}/api/projects/${projectId}/documents/${documentId}/download`;
}

// WebSocket helper
export function getWebSocketUrl(projectId: string): string {
  const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const baseUrl = API_BASE_URL.replace(/^https?:/, '');
  return `${wsProtocol}${baseUrl}/ws/${projectId}`;
}

