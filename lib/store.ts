/**
 * Zustand Store for AI-Powered Voice-Controlled Task & Project Manager
 * 
 * IMPORTANT FOR CLAUDE CODE:
 * - This store manages global state for voice interactions and real-time updates
 * - Voice session state should persist across browser sessions
 * - All state updates should trigger appropriate UI feedback
 * - Consider WebSocket connection state management
 * - Implement optimistic updates for better UX during voice processing
 * - Store should handle voice processing errors gracefully
 * 
 * Architecture:
 * - User state: Authentication and preferences
 * - Tasks/Projects: CRUD operations with voice metadata
 * - Voice session: Real-time recording and processing state
 * - Notifications: Real-time updates and alerts
 * - Theme: Dark/light mode preferences
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState, AppActions } from '@/types';

interface AppStore extends AppState, AppActions {}

const initialState: AppState = {
  user: null,
  tasks: [],
  projects: [],
  notifications: [],
  voiceSession: null,
  theme: 'light',
  isLoading: false,
  error: null,
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // User actions
      setUser: (user) => set({ user }),

      // Task actions
      addTask: (task) => set((state) => ({ 
        tasks: [...state.tasks, task] 
      })),

      updateTask: (updatedTask) => set((state) => ({
        tasks: state.tasks.map((task) => 
          task.id === updatedTask.id ? updatedTask : task
        ),
      })),

      deleteTask: (taskId) => set((state) => ({
        tasks: state.tasks.filter((task) => task.id !== taskId),
      })),

      // Project actions
      addProject: (project) => set((state) => ({
        projects: [...state.projects, project],
      })),

      updateProject: (updatedProject) => set((state) => ({
        projects: state.projects.map((project) =>
          project.id === updatedProject.id ? updatedProject : project
        ),
      })),

      deleteProject: (projectId) => set((state) => ({
        projects: state.projects.filter((project) => project.id !== projectId),
        // Also remove tasks associated with this project
        tasks: state.tasks.filter((task) => task.project_id !== projectId),
      })),

      // Notification actions
      addNotification: (notification) => set((state) => ({
        notifications: [notification, ...state.notifications],
      })),

      markNotificationRead: (notificationId) => set((state) => ({
        notifications: state.notifications.map((notification) =>
          notification.id === notificationId
            ? { ...notification, read: true }
            : notification
        ),
      })),

      // Voice session actions
      setVoiceSession: (session) => set({ voiceSession: session }),

      // Theme actions
      setTheme: (theme) => set({ theme }),

      // Loading and error actions
      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      // Utility actions
      clearError: () => set({ error: null }),

      clearNotifications: () => set({ notifications: [] }),

      // Computed getters
      getTasksByProject: (projectId: string) => {
        const state = get();
        return state.tasks.filter((task) => task.project_id === projectId);
      },

      getTasksByStatus: (status: string) => {
        const state = get();
        return state.tasks.filter((task) => task.status === status);
      },

      getUnreadNotifications: () => {
        const state = get();
        return state.notifications.filter((notification) => !notification.read);
      },

      getProjectById: (projectId: string) => {
        const state = get();
        return state.projects.find((project) => project.id === projectId);
      },

      getTaskById: (taskId: string) => {
        const state = get();
        return state.tasks.find((task) => task.id === taskId);
      },
    }),
    {
      name: 'voice-task-manager-storage',
      partialize: (state) => ({
        user: state.user,
        theme: state.theme,
        voice_preferences: state.user?.voice_preferences,
      }),
    }
  )
);
