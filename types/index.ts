/**
 * TypeScript type definitions for the AI-Powered Voice-Controlled Task & Project Manager
 * 
 * IMPORTANT FOR CLAUDE CODE:
 * - All types should be designed with voice interaction in mind
 * - Include confidence scores and metadata for voice processing
 * - Support real-time updates and WebSocket communication
 * - Consider accessibility requirements for voice-first interfaces
 * - All timestamps should be ISO 8601 format for consistency
 * - Voice metadata should capture processing context and user intent
 * 
 * This file contains all shared types used across the frontend and backend
 */

// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  voice_preferences: VoicePreferences;
  created_at: Date;
  updated_at: Date;
}

export interface VoicePreferences {
  language: string;
  speed: number;
  pitch: number;
  volume: number;
  auto_transcribe: boolean;
  voice_commands_enabled: boolean;
}

// Task Types
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: Date;
  project_id?: string;
  assigned_to?: string;
  created_by: string;
  tags: string[];
  voice_metadata?: VoiceMetadata;
  created_at: Date;
  updated_at: Date;
}

export interface VoiceMetadata {
  original_audio_url?: string;
  transcription?: string;
  intent?: string;
  confidence_score?: number;
  processing_time?: number;
  language?: string;
  voice_command?: string;
}

// Project Types
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'completed' | 'archived' | 'on_hold';
  members: ProjectMember[];
  created_by: string;
  color?: string;
  icon?: string;
  created_at: Date;
  updated_at: Date;
}

export interface ProjectMember {
  user_id: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joined_at: Date;
}

// Voice Processing Types
export interface VoiceCommand {
  id: string;
  command: string;
  description: string;
  category: 'task' | 'project' | 'system' | 'navigation';
  examples: string[];
  enabled: boolean;
}

export interface VoiceProcessingResult {
  success: boolean;
  transcription?: string;
  intent?: string;
  confidence?: number;
  entities?: Record<string, any>;
  response?: string;
  error?: string;
}

export interface VoiceSession {
  id: string;
  user_id: string;
  start_time: Date;
  end_time?: Date;
  commands_processed: number;
  total_duration: number;
  status: 'active' | 'ended' | 'error';
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'voice_input' | 'voice_response' | 'task_update' | 'project_update' | 'notification' | 'error';
  payload: any;
  timestamp: Date;
}

export interface VoiceInputMessage {
  audio_data: string;
  session_id: string;
  user_id: string;
}

export interface VoiceResponseMessage {
  transcription: string;
  intent: string;
  response: string;
  confidence: number;
  session_id: string;
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  type: 'task_assigned' | 'task_due' | 'project_update' | 'voice_processed' | 'system';
  title: string;
  message: string;
  read: boolean;
  data?: Record<string, any>;
  created_at: Date;
}

// Analytics Types
export interface VoiceAnalytics {
  total_commands: number;
  successful_commands: number;
  average_confidence: number;
  most_used_commands: Array<{ command: string; count: number }>;
  processing_time_stats: {
    average: number;
    min: number;
    max: number;
  };
  daily_usage: Array<{ date: string; commands: number }>;
}

// Form Types
export interface TaskFormData {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: Date;
  project_id?: string;
  assigned_to?: string;
  tags: string[];
}

export interface ProjectFormData {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  members: string[];
}

// Component Props Types
export interface VoiceRecorderProps {
  onVoiceInput: (audioData: string) => void;
  onProcessingComplete: (result: VoiceProcessingResult) => void;
  disabled?: boolean;
  className?: string;
}

export interface TaskCardProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onAssign: (taskId: string, userId: string) => void;
  className?: string;
}

export interface ProjectCardProps {
  project: Project;
  onUpdate: (project: Project) => void;
  onDelete: (projectId: string) => void;
  className?: string;
}

// Hook Types
export interface UseVoiceRecorderReturn {
  isRecording: boolean;
  isProcessing: boolean;
  startRecording: () => void;
  stopRecording: () => void;
  error: string | null;
  reset: () => void;
}

export interface UseVoiceCommandsReturn {
  commands: VoiceCommand[];
  executeCommand: (command: string) => Promise<VoiceProcessingResult>;
  isLoading: boolean;
  error: string | null;
}

// Store Types
export interface AppState {
  user: User | null;
  tasks: Task[];
  projects: Project[];
  notifications: Notification[];
  voiceSession: VoiceSession | null;
  theme: 'light' | 'dark';
  isLoading: boolean;
  error: string | null;
}

export interface AppActions {
  setUser: (user: User) => void;
  addTask: (task: Task) => void;
  updateTask: (task: Task) => void;
  deleteTask: (taskId: string) => void;
  addProject: (project: Project) => void;
  updateProject: (project: Project) => void;
  deleteProject: (projectId: string) => void;
  addNotification: (notification: Notification) => void;
  markNotificationRead: (notificationId: string) => void;
  setVoiceSession: (session: VoiceSession | null) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}
