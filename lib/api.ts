import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  Task, 
  Project, 
  VoiceProcessingResult, 
  VoiceCommand,
  ApiResponse,
  PaginatedResponse,
  TaskFormData,
  ProjectFormData,
  VoiceAnalytics
} from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  async register(userData: { email: string; password: string; name: string }): Promise<ApiResponse<User>> {
    const response = await this.client.post('/api/auth/register', userData);
    return response.data;
  }

  async login(credentials: { email: string; password: string }): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await this.client.post('/api/auth/login', credentials);
    return response.data;
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    const response = await this.client.post('/api/auth/refresh');
    return response.data;
  }

  async logout(): Promise<ApiResponse<void>> {
    const response = await this.client.post('/api/auth/logout');
    return response.data;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  // Voice processing endpoints
  async processVoice(audioData: string, sessionId?: string): Promise<ApiResponse<VoiceProcessingResult>> {
    const response = await this.client.post('/api/voice/process', {
      audio_data: audioData,
      session_id: sessionId,
    });
    return response.data;
  }

  async analyzeVoice(audioData: string): Promise<ApiResponse<VoiceProcessingResult>> {
    const response = await this.client.post('/api/voice/analyze', {
      audio_data: audioData,
    });
    return response.data;
  }

  async getVoiceCommands(): Promise<ApiResponse<VoiceCommand[]>> {
    const response = await this.client.get('/api/voice/commands');
    return response.data;
  }

  async submitVoiceFeedback(feedback: {
    session_id: string;
    transcription: string;
    was_correct: boolean;
    corrected_text?: string;
  }): Promise<ApiResponse<void>> {
    const response = await this.client.post('/api/voice/feedback', feedback);
    return response.data;
  }

  // Task management endpoints
  async getTasks(params?: {
    page?: number;
    limit?: number;
    status?: string;
    project_id?: string;
    assigned_to?: string;
    priority?: string;
  }): Promise<ApiResponse<PaginatedResponse<Task>>> {
    const response = await this.client.get('/api/tasks', { params });
    return response.data;
  }

  async createTask(taskData: TaskFormData): Promise<ApiResponse<Task>> {
    const response = await this.client.post('/api/tasks', taskData);
    return response.data;
  }

  async updateTask(taskId: string, taskData: Partial<TaskFormData>): Promise<ApiResponse<Task>> {
    const response = await this.client.put(`/api/tasks/${taskId}`, taskData);
    return response.data;
  }

  async deleteTask(taskId: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/api/tasks/${taskId}`);
    return response.data;
  }

  async assignTask(taskId: string, userId: string): Promise<ApiResponse<Task>> {
    const response = await this.client.post(`/api/tasks/${taskId}/assign`, {
      user_id: userId,
    });
    return response.data;
  }

  async completeTask(taskId: string): Promise<ApiResponse<Task>> {
    const response = await this.client.post(`/api/tasks/${taskId}/complete`);
    return response.data;
  }

  async getTaskById(taskId: string): Promise<ApiResponse<Task>> {
    const response = await this.client.get(`/api/tasks/${taskId}`);
    return response.data;
  }

  // Project management endpoints
  async getProjects(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<ApiResponse<PaginatedResponse<Project>>> {
    const response = await this.client.get('/api/projects', { params });
    return response.data;
  }

  async createProject(projectData: ProjectFormData): Promise<ApiResponse<Project>> {
    const response = await this.client.post('/api/projects', projectData);
    return response.data;
  }

  async updateProject(projectId: string, projectData: Partial<ProjectFormData>): Promise<ApiResponse<Project>> {
    const response = await this.client.put(`/api/projects/${projectId}`, projectData);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/api/projects/${projectId}`);
    return response.data;
  }

  async getProjectStatus(projectId: string): Promise<ApiResponse<{
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    progress_percentage: number;
    recent_activity: any[];
  }>> {
    const response = await this.client.get(`/api/projects/${projectId}/status`);
    return response.data;
  }

  async addProjectMember(projectId: string, userId: string, role: string): Promise<ApiResponse<Project>> {
    const response = await this.client.post(`/api/projects/${projectId}/members`, {
      user_id: userId,
      role,
    });
    return response.data;
  }

  async getProjectById(projectId: string): Promise<ApiResponse<Project>> {
    const response = await this.client.get(`/api/projects/${projectId}`);
    return response.data;
  }

  // Analytics endpoints
  async getVoiceAnalytics(timeRange?: string): Promise<ApiResponse<VoiceAnalytics>> {
    const response = await this.client.get('/api/analytics/voice', {
      params: { time_range: timeRange },
    });
    return response.data;
  }

  async getTaskAnalytics(projectId?: string): Promise<ApiResponse<{
    total_tasks: number;
    completed_tasks: number;
    overdue_tasks: number;
    tasks_by_priority: Record<string, number>;
    tasks_by_status: Record<string, number>;
    completion_trend: Array<{ date: string; completed: number }>;
  }>> {
    const response = await this.client.get('/api/analytics/tasks', {
      params: { project_id: projectId },
    });
    return response.data;
  }

  // File upload endpoints
  async uploadFile(file: File, type: 'voice' | 'attachment'): Promise<ApiResponse<{ url: string; filename: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await this.client.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Notification endpoints
  async getNotifications(params?: {
    page?: number;
    limit?: number;
    unread_only?: boolean;
  }): Promise<ApiResponse<PaginatedResponse<any>>> {
    const response = await this.client.get('/api/notifications', { params });
    return response.data;
  }

  async markNotificationRead(notificationId: string): Promise<ApiResponse<void>> {
    const response = await this.client.put(`/api/notifications/${notificationId}/read`);
    return response.data;
  }

  async markAllNotificationsRead(): Promise<ApiResponse<void>> {
    const response = await this.client.put('/api/notifications/read-all');
    return response.data;
  }

  // User preferences endpoints
  async updateVoicePreferences(preferences: any): Promise<ApiResponse<User>> {
    const response = await this.client.put('/api/user/voice-preferences', preferences);
    return response.data;
  }

  async updateProfile(profileData: Partial<User>): Promise<ApiResponse<User>> {
    const response = await this.client.put('/api/user/profile', profileData);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    const response = await this.client.get('/api/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
