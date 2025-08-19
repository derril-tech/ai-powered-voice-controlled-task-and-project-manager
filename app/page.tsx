'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  Users, 
  BarChart3, 
  Settings,
  Bell,
  Sun,
  Moon,
  Menu,
  X
} from 'lucide-react';
import VoiceRecorder from '@/components/VoiceRecorder';
import TaskList from '@/components/TaskList';
import ProjectDashboard from '@/components/ProjectDashboard';
import VoiceCommands from '@/components/VoiceCommands';
import NotificationCenter from '@/components/NotificationCenter';
import { useAppStore } from '@/lib/store';
import { useTheme } from '@/components/ThemeProvider';
import { VoiceProcessingResult } from '@/types';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const { theme, setTheme } = useTheme();
  const { 
    user, 
    tasks, 
    projects, 
    notifications, 
    addTask, 
    addProject, 
    addNotification,
    getUnreadNotifications 
  } = useAppStore();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'tasks' | 'projects' | 'voice'>('tasks');
  const [searchQuery, setSearchQuery] = useState('');
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);

  const unreadNotifications = getUnreadNotifications();

  // Handle voice processing
  const handleVoiceProcessingComplete = (result: VoiceProcessingResult) => {
    setIsProcessingVoice(false);
    
    if (result.success) {
      toast.success('Voice command processed successfully!');
      
      // Handle different voice commands
      if (result.intent === 'create_task') {
        // Create task from voice input
        const newTask = {
          id: Date.now().toString(),
          title: result.transcription || 'New Task',
          description: '',
          status: 'pending' as const,
          priority: 'medium' as const,
          created_by: user?.id || '',
          tags: [],
          created_at: new Date(),
          updated_at: new Date(),
        };
        addTask(newTask);
        toast.success('Task created from voice command!');
      } else if (result.intent === 'create_project') {
        // Create project from voice input
        const newProject = {
          id: Date.now().toString(),
          name: result.transcription || 'New Project',
          description: '',
          status: 'active' as const,
          members: [],
          created_by: user?.id || '',
          created_at: new Date(),
          updated_at: new Date(),
        };
        addProject(newProject);
        toast.success('Project created from voice command!');
      }
    } else {
      toast.error(result.error || 'Failed to process voice command');
    }
  };

  const handleVoiceInput = (audioData: string) => {
    setIsProcessingVoice(true);
    // The actual processing is handled by the VoiceRecorder component
  };

  // Filter tasks based on search query
  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Filter projects based on search query
  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Title */}
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AI</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Voice Task Manager
                </h1>
              </div>
            </div>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-lg mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search tasks, projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              {/* Voice Recorder */}
              <div className="relative">
                <VoiceRecorder
                  onVoiceInput={handleVoiceInput}
                  onProcessingComplete={handleVoiceProcessingComplete}
                  disabled={isProcessingVoice}
                  className="scale-75"
                />
              </div>

              {/* Notifications */}
              <button className="relative p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <Bell className="h-6 w-6" />
                {unreadNotifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadNotifications.length}
                  </span>
                )}
              </button>

              {/* Theme Toggle */}
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                {theme === 'dark' ? <Sun className="h-6 w-6" /> : <Moon className="h-6 w-6" />}
              </button>

              {/* User Menu */}
              <div className="relative">
                <button className="flex items-center space-x-2 p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium text-sm">
                      {user?.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Navigation</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 text-gray-400 hover:text-gray-500"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <nav className="mt-6 px-6">
            <div className="space-y-2">
              <button
                onClick={() => setActiveTab('tasks')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'tasks'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Calendar className="h-5 w-5" />
                <span>Tasks</span>
                <span className="ml-auto bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-2 py-1 rounded-full">
                  {tasks.length}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('projects')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'projects'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Users className="h-5 w-5" />
                <span>Projects</span>
                <span className="ml-auto bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-2 py-1 rounded-full">
                  {projects.length}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('voice')}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeTab === 'voice'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <BarChart3 className="h-5 w-5" />
                <span>Voice Commands</span>
              </button>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
              <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <Settings className="h-5 w-5" />
                <span>Settings</span>
              </button>
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'tasks' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Tasks</h2>
                    <button className="btn-primary flex items-center space-x-2">
                      <Plus className="h-4 w-4" />
                      <span>Add Task</span>
                    </button>
                  </div>
                  <TaskList tasks={filteredTasks} />
                </div>
              )}

              {activeTab === 'projects' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Projects</h2>
                    <button className="btn-primary flex items-center space-x-2">
                      <Plus className="h-4 w-4" />
                      <span>Add Project</span>
                    </button>
                  </div>
                  <ProjectDashboard projects={filteredProjects} />
                </div>
              )}

              {activeTab === 'voice' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Voice Commands</h2>
                  </div>
                  <VoiceCommands />
                </div>
              )}
            </motion.div>
          </div>
        </main>
      </div>

      {/* Notification Center */}
      <NotificationCenter notifications={notifications} />

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
