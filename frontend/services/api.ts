/**
 * API Service for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ProcessResponse {
  record_id: string;
  timestamp: string;
  mood?: {
    type?: string;
    intensity?: number;
    keywords: string[];
  };
  inspirations: Array<{
    core_idea: string;
    tags: string[];
    category: string;
  }>;
  todos: Array<{
    task: string;
    time?: string;
    location?: string;
    status: string;
  }>;
  error?: string;
}

export interface RecordResponse {
  records: Array<{
    record_id: string;
    timestamp: string;
    input_type: 'audio' | 'text';
    original_text: string;
    parsed_data: {
      mood?: any;
      inspirations: any[];
      todos: any[];
    };
  }>;
}

export interface MoodResponse {
  moods: Array<{
    record_id: string;
    timestamp: string;
    type?: string;
    intensity?: number;
    keywords: string[];
  }>;
}

export interface InspirationResponse {
  inspirations: Array<{
    record_id: string;
    timestamp: string;
    core_idea: string;
    tags: string[];
    category: string;
  }>;
}

export interface TodoResponse {
  todos: Array<{
    record_id: string;
    timestamp: string;
    task: string;
    time?: string;
    location?: string;
    status: string;
  }>;
}

export interface UserConfigResponse {
  user_id: string;
  created_at: string;
  character: {
    image_url?: string;
    prompt?: string;
    revised_prompt?: string;
    preferences: {
      color: string;
      personality: string;
      appearance: string;
      role: string;
    };
    generated_at?: string;
    generation_count: number;
  };
  settings: {
    theme: string;
    language: string;
  };
}

class APIService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Process audio or text input
   */
  async processInput(audio?: File, text?: string): Promise<ProcessResponse> {
    const formData = new FormData();
    
    if (audio) {
      formData.append('audio', audio);
    } else if (text) {
      formData.append('text', text);
    } else {
      throw new Error('Either audio or text must be provided');
    }

    const response = await fetch(`${this.baseUrl}/api/process`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to process input');
    }

    return response.json();
  }

  /**
   * Get all records
   */
  async getRecords(): Promise<RecordResponse> {
    const response = await fetch(`${this.baseUrl}/api/records`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch records');
    }

    return response.json();
  }

  /**
   * Get all moods
   */
  async getMoods(): Promise<MoodResponse> {
    const response = await fetch(`${this.baseUrl}/api/moods`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch moods');
    }

    return response.json();
  }

  /**
   * Get all inspirations
   */
  async getInspirations(): Promise<InspirationResponse> {
    const response = await fetch(`${this.baseUrl}/api/inspirations`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch inspirations');
    }

    return response.json();
  }

  /**
   * Get all todos
   */
  async getTodos(): Promise<TodoResponse> {
    const response = await fetch(`${this.baseUrl}/api/todos`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch todos');
    }

    return response.json();
  }

  /**
   * Update todo status
   */
  async updateTodoStatus(todoId: string, status: string): Promise<{ success: boolean }> {
    const formData = new FormData();
    formData.append('status', status);

    const response = await fetch(`${this.baseUrl}/api/todos/${todoId}`, {
      method: 'PATCH',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to update todo');
    }

    return response.json();
  }

  /**
   * Get user configuration
   */
  async getUserConfig(): Promise<UserConfigResponse> {
    const response = await fetch(`${this.baseUrl}/api/user/config`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch user config');
    }

    return response.json();
  }

  /**
   * Chat with AI assistant
   */
  async chatWithAI(message: string): Promise<string> {
    const formData = new FormData();
    formData.append('text', message);

    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to chat with AI');
    }

    const data = await response.json();
    return data.response || '抱歉，我现在有点累了，稍后再聊好吗？';
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  /**
   * Generate character image
   */
  async generateCharacter(preferences: {
    color: string;
    personality: string;
    appearance: string;
    role: string;
  }): Promise<{
    success: boolean;
    image_url: string;
    prompt: string;
    preferences: any;
    task_id?: string;
  }> {
    const formData = new FormData();
    formData.append('color', preferences.color);
    formData.append('personality', preferences.personality);
    formData.append('appearance', preferences.appearance);
    formData.append('role', preferences.role);

    const response = await fetch(`${this.baseUrl}/api/character/generate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.error || 'Failed to generate character');
    }

    return response.json();
  }

  /**
   * Update character preferences
   */
  async updateCharacterPreferences(preferences: {
    color?: string;
    personality?: string;
    appearance?: string;
    role?: string;
  }): Promise<{ success: boolean; preferences: any }> {
    const formData = new FormData();
    if (preferences.color) formData.append('color', preferences.color);
    if (preferences.personality) formData.append('personality', preferences.personality);
    if (preferences.appearance) formData.append('appearance', preferences.appearance);
    if (preferences.role) formData.append('role', preferences.role);

    const response = await fetch(`${this.baseUrl}/api/character/preferences`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to update preferences');
    }

    return response.json();
  }
}

export const apiService = new APIService();
