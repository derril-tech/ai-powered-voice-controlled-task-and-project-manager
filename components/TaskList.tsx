'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  Calendar, 
  Tag, 
  User, 
  MoreVertical,
  Edit,
  Trash2,
  Flag,
  MessageSquare
} from 'lucide-react';
import { Task } from '@/types';
import { formatDate, getPriorityColor, getStatusColor, cn } from '@/lib/utils';

interface TaskListProps {
  tasks: Task[];
}

const TaskList: React.FC<TaskListProps> = ({ tasks }) => {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all');

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-500" />;
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <Flag className="h-4 w-4 text-red-500" />;
      case 'high':
        return <Flag className="h-4 w-4 text-orange-500" />;
      case 'medium':
        return <Flag className="h-4 w-4 text-yellow-500" />;
      default:
        return <Flag className="h-4 w-4 text-green-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex space-x-2">
          {(['all', 'pending', 'in_progress', 'completed'] as const).map((filterOption) => (
            <button
              key={filterOption}
              onClick={() => setFilter(filterOption)}
              className={cn(
                'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                filter === filterOption
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              )}
            >
              {filterOption.charAt(0).toUpperCase() + filterOption.slice(1).replace('_', ' ')}
              <span className="ml-1 text-xs">
                ({tasks.filter(t => filterOption === 'all' ? true : t.status === filterOption).length})
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredTasks.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-12"
            >
              <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No tasks found
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                {filter === 'all' 
                  ? 'Create your first task to get started!' 
                  : `No ${filter.replace('_', ' ')} tasks found.`
                }
              </p>
            </motion.div>
          ) : (
            filteredTasks.map((task) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="task-card bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Status Icon */}
                    <button className="mt-1">
                      {getStatusIcon(task.status)}
                    </button>

                    {/* Task Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className={cn(
                            "text-lg font-medium text-gray-900 dark:text-white mb-2",
                            task.status === 'completed' && "line-through text-gray-500 dark:text-gray-400"
                          )}>
                            {task.title}
                          </h3>
                          
                          {task.description && (
                            <p className="text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
                              {task.description}
                            </p>
                          )}

                          {/* Task Meta */}
                          <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                            {task.due_date && (
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>Due {formatDate(task.due_date)}</span>
                              </div>
                            )}
                            
                            {task.assigned_to && (
                              <div className="flex items-center space-x-1">
                                <User className="h-4 w-4" />
                                <span>Assigned</span>
                              </div>
                            )}

                            {task.voice_metadata && (
                              <div className="flex items-center space-x-1">
                                <MessageSquare className="h-4 w-4" />
                                <span>Voice created</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Priority and Actions */}
                        <div className="flex items-center space-x-2 ml-4">
                          {getPriorityIcon(task.priority)}
                          
                          <div className="relative">
                            <button
                              onClick={() => setSelectedTask(selectedTask === task.id ? null : task.id)}
                              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
                            >
                              <MoreVertical className="h-4 w-4" />
                            </button>

                            {/* Dropdown Menu */}
                            <AnimatePresence>
                              {selectedTask === task.id && (
                                <motion.div
                                  initial={{ opacity: 0, scale: 0.95 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  exit={{ opacity: 0, scale: 0.95 }}
                                  className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10"
                                >
                                  <button className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                                    <Edit className="h-4 w-4" />
                                    <span>Edit</span>
                                  </button>
                                  <button className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20">
                                    <Trash2 className="h-4 w-4" />
                                    <span>Delete</span>
                                  </button>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        </div>
                      </div>

                      {/* Tags */}
                      {task.tags.length > 0 && (
                        <div className="flex items-center space-x-2 mt-3">
                          {task.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                            >
                              <Tag className="h-3 w-3 mr-1" />
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Status and Priority Badges */}
                      <div className="flex items-center space-x-2 mt-3">
                        <span className={cn("status-indicator", getStatusColor(task.status))}>
                          {task.status.replace('_', ' ')}
                        </span>
                        <span className={cn("status-indicator", getPriorityColor(task.priority))}>
                          {task.priority}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default TaskList;
