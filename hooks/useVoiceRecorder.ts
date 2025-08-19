/**
 * Custom React Hooks for Voice Recording and Processing
 * 
 * IMPORTANT FOR CLAUDE CODE:
 * - These hooks handle the core voice interaction functionality
 * - Implement proper error handling for microphone access and recording failures
 * - Support real-time audio processing and WebSocket communication
 * - Consider accessibility requirements (screen reader announcements)
 * - Handle different audio formats and quality settings
 * - Implement proper cleanup to prevent memory leaks
 * - Support voice command recognition and intent extraction
 * 
 * Voice Processing Pipeline:
 * 1. Audio capture via MediaRecorder API
 * 2. Real-time streaming to backend via WebSocket
 * 3. Speech-to-text conversion with confidence scoring
 * 4. Intent recognition and entity extraction
 * 5. Action execution and response generation
 * 6. Real-time feedback to user
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { UseVoiceRecorderReturn } from '@/types';
import { apiClient } from '@/lib/api';

export const useVoiceRecorder = (): UseVoiceRecorderReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);

  // Check if browser supports speech recognition
  const isSpeechRecognitionSupported = typeof window !== 'undefined' && 
    ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);

  // Initialize speech recognition
  useEffect(() => {
    if (isSpeechRecognitionSupported && !recognitionRef.current) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
    }
  }, [isSpeechRecognitionSupported]);

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Initialize MediaRecorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });
      
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = async () => {
        setIsProcessing(true);
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const audioData = await blobToBase64(audioBlob);
          
          // Process voice with backend
          const response = await apiClient.processVoice(audioData);
          
          if (response.success && response.data) {
            // Handle successful voice processing
            console.log('Voice processed:', response.data);
          } else {
            setError(response.error || 'Failed to process voice input');
          }
        } catch (err) {
          setError('Error processing voice input');
          console.error('Voice processing error:', err);
        } finally {
          setIsProcessing(false);
        }
      };
      
      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);
      
      // Start speech recognition if available
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
      
    } catch (err) {
      setError('Failed to start recording. Please check microphone permissions.');
      console.error('Recording start error:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      
      // Stop all tracks
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    }
  }, [isRecording]);

  const reset = useCallback(() => {
    setIsRecording(false);
    setIsProcessing(false);
    setError(null);
    audioChunksRef.current = [];
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    error,
    reset,
  };
};

// Utility function to convert blob to base64
const blobToBase64 = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data URL prefix
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

// Extended hook with speech recognition events
export const useVoiceRecorderWithRecognition = () => {
  const voiceRecorder = useVoiceRecorder();
  const [transcription, setTranscription] = useState('');
  const [interimTranscription, setInterimTranscription] = useState('');
  const [confidence, setConfidence] = useState(0);

  useEffect(() => {
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          const confidence = event.results[i][0].confidence;
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
            setConfidence(confidence);
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscription(finalTranscript);
        setInterimTranscription(interimTranscript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        voiceRecorder.setError?.(`Speech recognition error: ${event.error}`);
      };
      
      recognition.onend = () => {
        // Restart recognition if still recording
        if (voiceRecorder.isRecording) {
          recognition.start();
        }
      };
    }
  }, [voiceRecorder.isRecording]);

  return {
    ...voiceRecorder,
    transcription,
    interimTranscription,
    confidence,
  };
};
