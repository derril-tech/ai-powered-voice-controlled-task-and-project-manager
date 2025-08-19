'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Mic, 
  Play, 
  Volume2, 
  Settings, 
  BookOpen, 
  Zap,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import { VoiceCommand } from '@/types';
import { apiClient } from '@/lib/api';

const VoiceCommands: React.FC = () => {
  const [commands, setCommands] = useState<VoiceCommand[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadVoiceCommands();
  }, []);

  const loadVoiceCommands = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getVoiceCommands();
      if (response.success && response.data) {
        setCommands(response.data);
      }
    } catch (error) {
      console.error('Failed to load voice commands:', error);
    } finally {
      setLoading(false);
    }
  };

  // Default commands if API is not available
  const defaultCommands: VoiceCommand[] = [
    {
      id: '1',
      command: 'Create task',
      description: 'Create a new task with voice input',
      category: 'task',
      examples: [
        'Create a task to buy groceries',
        'Add a new task for the meeting tomorrow',
        'Create task: follow up with client'
      ],
      enabled: true
    },
    {
      id: '2',
      command: 'Create project',
      description: 'Create a new project',
      category: 'project',
      examples: [
        'Create a new project called Website Redesign',
        'Start a project for Q4 planning',
        'Create project: Marketing Campaign'
      ],
      enabled: true
    },
    {
      id: '3',
      command: 'Mark task complete',
      description: 'Mark a task as completed',
      category: 'task',
      examples: [
        'Mark the grocery shopping task as complete',
        'Complete the meeting preparation task',
        'Mark task done: client follow up'
      ],
      enabled: true
    },
    {
      id: '4',
      command: 'Show tasks',
      description: 'Display all tasks or filtered tasks',
      category: 'navigation',
      examples: [
        'Show all my tasks',
        'Show pending tasks',
        'Show tasks for today'
      ],
      enabled: true
    },
    {
      id: '5',
      command: 'Show projects',
      description: 'Display all projects or project details',
      category: 'navigation',
      examples: [
        'Show all projects',
        'Show active projects',
        'Show project status for Website Redesign'
      ],
      enabled: true
    },
    {
      id: '6',
      command: 'Assign task',
      description: 'Assign a task to a team member',
      category: 'task',
      examples: [
        'Assign the design task to Sarah',
        'Give the coding task to John',
        'Assign task to David: review the proposal'
      ],
      enabled: true
    },
    {
      id: '7',
      command: 'Set priority',
      description: 'Set priority level for a task',
      category: 'task',
      examples: [
        'Set high priority for the urgent task',
        'Make the client meeting urgent priority',
        'Set priority low for the documentation task'
      ],
      enabled: true
    },
    {
      id: '8',
      command: 'Add due date',
      description: 'Set a due date for a task',
      category: 'task',
      examples: [
        'Set due date for the report to next Friday',
        'Add due date: finish the design by tomorrow',
        'Set deadline for the project to end of month'
      ],
      enabled: true
    }
  ];

  const displayCommands = commands.length > 0 ? commands : defaultCommands;

  const categories = ['all', 'task', 'project', 'navigation', 'system'];
  
  const filteredCommands = displayCommands.filter(command => {
    const matchesCategory = selectedCategory === 'all' || command.category === selectedCategory;
    const matchesSearch = command.command.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         command.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'task':
        return <CheckCircle className="h-5 w-5" />;
      case 'project':
        return <BookOpen className="h-5 w-5" />;
      case 'navigation':
        return <Zap className="h-5 w-5" />;
      case 'system':
        return <Settings className="h-5 w-5" />;
      default:
        return <Mic className="h-5 w-5" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'task':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'project':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'navigation':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'system':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Clock className="h-8 w-8 text-gray-400 animate-spin" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Loading voice commands...
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Preparing your voice interface
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-700">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Mic className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Voice Commands
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Use these voice commands to control your tasks and projects
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <Volume2 className="h-4 w-4" />
            <span>Click the microphone button to start</span>
          </div>
          <div className="flex items-center space-x-1">
            <Play className="h-4 w-4" />
            <span>Speak clearly and naturally</span>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search voice commands..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="flex space-x-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Commands Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCommands.map((command) => (
          <motion.div
            key={command.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="voice-command"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getCategoryColor(command.category)}`}>
                  {getCategoryIcon(command.category)}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {command.command}
                  </h3>
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(command.category)}`}>
                    {command.category}
                  </span>
                </div>
              </div>
              
              <div className={`w-3 h-3 rounded-full ${command.enabled ? 'bg-green-500' : 'bg-gray-300'}`} />
            </div>

            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
              {command.description}
            </p>

            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Examples:
              </h4>
              <div className="space-y-2">
                {command.examples.map((example, index) => (
                  <div
                    key={index}
                    className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border-l-4 border-blue-500"
                  >
                    "{example}"
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Status: {command.enabled ? 'Active' : 'Disabled'}</span>
                <div className="flex items-center space-x-1">
                  {command.enabled ? (
                    <CheckCircle className="h-3 w-3 text-green-500" />
                  ) : (
                    <AlertCircle className="h-3 w-3 text-gray-400" />
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredCommands.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <Mic className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No voice commands found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Try adjusting your search or filter criteria
          </p>
        </div>
      )}

      {/* Tips Section */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center flex-shrink-0">
            <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          </div>
          <div>
            <h3 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">
              Voice Command Tips
            </h3>
            <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
              <li>• Speak clearly and at a normal pace</li>
              <li>• Use natural language - "Create a task to buy groceries"</li>
              <li>• Be specific with names and dates</li>
              <li>• Wait for the processing indicator before speaking again</li>
              <li>• Ensure your microphone has proper permissions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceCommands;
