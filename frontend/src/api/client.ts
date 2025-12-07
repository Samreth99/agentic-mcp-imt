const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
  success: boolean;
}

export interface HealthResponse {
  status: string;
  agent_initialized: boolean;
  version: string;
}

export interface ErrorResponse {
  detail: string;
  success: boolean;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  }

  async ask(message: string): Promise<ChatResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/ask?message=${encodeURIComponent(message)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  async readinessCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health/ready`);
    
    if (!response.ok) {
      throw new Error('Readiness check failed');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
export default apiClient;
