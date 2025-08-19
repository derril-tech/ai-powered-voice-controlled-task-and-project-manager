'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Loader2, Volume2, AlertCircle, CheckCircle } from 'lucide-react';
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder';
import { VoiceRecorderProps, VoiceProcessingResult } from '@/types';
import { cn } from '@/lib/utils';

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onVoiceInput,
  onProcessingComplete,
  disabled = false,
  className,
}) => {
  const {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    error,
    reset,
  } = useVoiceRecorder();

  const [recordingTime, setRecordingTime] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');

  // Timer for recording duration
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  // Handle recording start
  const handleStartRecording = async () => {
    try {
      await startRecording();
      setShowFeedback(false);
      setFeedbackMessage('');
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  // Handle recording stop
  const handleStopRecording = () => {
    stopRecording();
  };

  // Handle processing complete
  const handleProcessingComplete = (result: VoiceProcessingResult) => {
    onProcessingComplete(result);
    if (result.success) {
      setFeedbackMessage('Voice command processed successfully!');
      setShowFeedback(true);
      setTimeout(() => setShowFeedback(false), 3000);
    } else {
      setFeedbackMessage(result.error || 'Failed to process voice command');
      setShowFeedback(true);
      setTimeout(() => setShowFeedback(false), 3000);
    }
  };

  // Format recording time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Voice wave animation bars
  const VoiceWaveBars = () => (
    <div className="flex items-center justify-center space-x-1">
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          className="w-1 bg-white rounded-full"
          animate={{
            height: isRecording ? [4, 20, 4] : 4,
          }}
          transition={{
            duration: 0.8,
            repeat: isRecording ? Infinity : 0,
            delay: i * 0.1,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );

  return (
    <div className={cn('relative', className)}>
      {/* Main Voice Recorder Button */}
      <motion.div
        className={cn(
          'relative flex flex-col items-center justify-center w-24 h-24 rounded-full cursor-pointer transition-all duration-300',
          'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700',
          'shadow-lg hover:shadow-xl',
          isRecording && 'shadow-voice-active scale-110',
          isProcessing && 'bg-gradient-to-r from-orange-500 to-yellow-500',
          disabled && 'opacity-50 cursor-not-allowed',
          error && 'bg-gradient-to-r from-red-500 to-pink-500'
        )}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
        onClick={disabled ? undefined : (isRecording ? handleStopRecording : handleStartRecording)}
      >
        {/* Recording Indicator */}
        {isRecording && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-white/30"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}

        {/* Icon */}
        <div className="relative z-10">
          {isProcessing ? (
            <Loader2 className="w-8 h-8 text-white animate-spin" />
          ) : isRecording ? (
            <MicOff className="w-8 h-8 text-white" />
          ) : (
            <Mic className="w-8 h-8 text-white" />
          )}
        </div>

        {/* Voice Wave Animation */}
        {isRecording && (
          <motion.div
            className="absolute -bottom-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <VoiceWaveBars />
          </motion.div>
        )}
      </motion.div>

      {/* Recording Timer */}
      {isRecording && (
        <motion.div
          className="absolute -bottom-12 left-1/2 transform -translate-x-1/2"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <span className="text-sm font-mono text-gray-600 dark:text-gray-300">
            {formatTime(recordingTime)}
          </span>
        </motion.div>
      )}

      {/* Status Messages */}
      <AnimatePresence>
        {isRecording && (
          <motion.div
            className="absolute -top-12 left-1/2 transform -translate-x-1/2"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="flex items-center space-x-2 px-3 py-1 bg-blue-100 dark:bg-blue-900 rounded-full">
              <Volume2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-pulse" />
              <span className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                Listening...
              </span>
            </div>
          </motion.div>
        )}

        {isProcessing && (
          <motion.div
            className="absolute -top-12 left-1/2 transform -translate-x-1/2"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="flex items-center space-x-2 px-3 py-1 bg-orange-100 dark:bg-orange-900 rounded-full">
              <Loader2 className="w-4 h-4 text-orange-600 dark:text-orange-400 animate-spin" />
              <span className="text-sm text-orange-600 dark:text-orange-400 font-medium">
                Processing...
              </span>
            </div>
          </motion.div>
        )}

        {showFeedback && (
          <motion.div
            className="absolute -top-12 left-1/2 transform -translate-x-1/2"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className={cn(
              'flex items-center space-x-2 px-3 py-1 rounded-full',
              feedbackMessage.includes('successfully') 
                ? 'bg-green-100 dark:bg-green-900' 
                : 'bg-red-100 dark:bg-red-900'
            )}>
              {feedbackMessage.includes('successfully') ? (
                <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
              )}
              <span className={cn(
                'text-sm font-medium',
                feedbackMessage.includes('successfully')
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'
              )}>
                {feedbackMessage}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Display */}
      {error && (
        <motion.div
          className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 w-64"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <div className="flex items-center space-x-2 px-3 py-2 bg-red-100 dark:bg-red-900 rounded-lg">
            <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0" />
            <span className="text-sm text-red-600 dark:text-red-400">
              {error}
            </span>
          </div>
        </motion.div>
      )}

      {/* Instructions */}
      {!isRecording && !isProcessing && !error && (
        <motion.div
          className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 w-48 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Click to start recording
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default VoiceRecorder;
