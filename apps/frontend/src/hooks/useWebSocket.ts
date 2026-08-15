import { useState, useEffect, useRef, useCallback } from 'react';

export interface PlanStep {
  id: number;
  description: string;
  tool_name: string;
  arguments: Record<string, any>;
  status: 'pending' | 'executing' | 'waiting_for_permission' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

export interface PermissionRequest {
  step: PlanStep;
  risk_level: string;
  tool_name: string;
  arguments: Record<string, any>;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'info' | 'success' | 'warn' | 'error';
  message: string;
}

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [agentState, setAgentState] = useState<string>('IDLE');
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentPlan, setCurrentPlan] = useState<PlanStep[]>([]);
  const [permissionReq, setPermissionReq] = useState<PermissionRequest | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [systemStats, setSystemStats] = useState<Record<string, any>>({});

  // Voice State (Phase 2 Real Microphone + Speech Synthesis)
  const [partialTranscript, setPartialTranscript] = useState<string>('');
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [isListeningVoice, setIsListeningVoice] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<any>(null);

  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    setLogs((prev) => [
      {
        id: Math.random().toString(36).substring(2, 9),
        timestamp: new Date().toLocaleTimeString(),
        type,
        message,
      },
      ...prev.slice(0, 99),
    ]);
  }, []);

  // Speak text response via browser SpeechSynthesis
  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // stop previous speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }, []);

  // Stop active speech playback
  const interruptSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    fetch('/api/voice/interrupt', { method: 'POST' }).catch(() => {});
    addLog('Interrupted speech playback', 'warn');
  }, [addLog]);

  // Send Command to Backend Orchestrator
  const sendCommand = useCallback(async (command: string) => {
    try {
      addLog(`Command: "${command}"`, 'info');
      setAgentState('UNDERSTANDING');
      
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      return data;
    } catch (err: any) {
      addLog(`Failed to communicate with engine: ${err.message}`, 'error');
      setAgentState('ERROR');
    }
  }, [addLog]);

  // Initialize Browser Microphone Speech Recognition (Web Speech API)
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListeningVoice(true);
        addLog('Microphone listening active. Speak into your mic...', 'info');
      };

      recognition.onresult = (event: any) => {
        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalText += transcript;
          } else {
            interimText += transcript;
          }
        }

        if (interimText) {
          setPartialTranscript(interimText);
        }

        if (finalText.trim()) {
          const cleanCmd = finalText.trim();
          setPartialTranscript(cleanCmd);
          addLog(`Voice Picked Up: "${cleanCmd}"`, 'success');

          // Check fast-path voice interruptions
          const lower = cleanCmd.toLowerCase();
          if (lower.includes('stop talking') || lower.includes('be quiet') || lower.includes('shut up')) {
            interruptSpeaking();
          } else if (lower.includes('cancel task') || lower === 'cancel') {
            fetch('/api/tasks/cancel', { method: 'POST' }).catch(() => {});
          } else {
            sendCommand(cleanCmd);
          }
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          console.warn('Speech recognition status:', event.error);
        }
      };

      recognition.onend = () => {
        setIsListeningVoice(false);
        // Auto-restart if not muted
        if (!isMuted && recognitionRef.current) {
          try {
            recognition.start();
          } catch (e) {
            // ignore
          }
        }
      };

      recognitionRef.current = recognition;
      try {
        recognition.start();
      } catch (e) {}
    } else {
      addLog('Browser Web Speech API not supported in this browser. Use Chrome/Edge/Brave for microphone input.', 'warn');
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, [addLog, isMuted, sendCommand, interruptSpeaking]);

  // WebSocket Connection Lifecycle
  useEffect(() => {
    let socket: WebSocket;
    let reconnectTimeout: any;

    const connect = () => {
      const hostname = window.location.hostname || '127.0.0.1';
      const wsUrl = `ws://${hostname}:8000/api/ws`;

      socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        addLog('Connected to AURA OS Voice & Shell Engine', 'info');
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: evtType, state, task_id, data } = payload;

          if (state) setAgentState(state);
          if (task_id) setCurrentTaskId(task_id);

          switch (evtType) {
            case 'connection_established':
              addLog(`Engine ready in state: ${state}`, 'info');
              break;

            case 'state_change':
              addLog(`State changed to: ${state}`, 'info');
              if (state === 'COMPLETED') {
                speakText('Task completed successfully.');
              }
              if (state === 'IDLE' || state === 'COMPLETED' || state === 'FAILED' || state === 'CANCELLED') {
                setPermissionReq(null);
                setPartialTranscript('');
              }
              break;

            case 'plan_update':
              if (data?.plan) {
                setCurrentPlan(data.plan);
                addLog(`Generated task plan with ${data.plan.length} steps`, 'info');
              }
              break;

            case 'tool_log':
              if (data?.step) {
                addLog(`Executed [${data.step.tool_name}] — Success`, 'success');
              }
              break;

            case 'permission_required':
              setPermissionReq(data);
              addLog(`Action requires permission confirmation: Risk Level [${data?.risk_level}]`, 'warn');
              speakText('Security permission required for this action.');
              break;

            case 'system_stats':
              setSystemStats(data);
              break;
          }
        } catch (err) {
          console.error('Error parsing WebSocket payload:', err);
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      };

      socket.onerror = () => {
        setIsConnected(false);
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (socket) socket.close();
    };
  }, [addLog, speakText]);

  const approvePermission = async () => {
    try {
      setPermissionReq(null);
      await fetch('/api/permissions/approve', { method: 'POST' });
      addLog('User approved permission request', 'success');
    } catch (err: any) {
      addLog(`Failed to approve permission: ${err.message}`, 'error');
    }
  };

  const rejectPermission = async () => {
    try {
      setPermissionReq(null);
      await fetch('/api/permissions/reject', { method: 'POST' });
      addLog('User rejected permission request', 'warn');
    } catch (err: any) {
      addLog(`Failed to reject permission: ${err.message}`, 'error');
    }
  };

  const toggleMute = async () => {
    const nextMute = !isMuted;
    setIsMuted(nextMute);
    
    if (recognitionRef.current) {
      if (nextMute) {
        try { recognitionRef.current.stop(); } catch(e){}
      } else {
        try { recognitionRef.current.start(); } catch(e){}
      }
    }

    const endpoint = nextMute ? '/api/voice/mute' : '/api/voice/unmute';
    await fetch(endpoint, { method: 'POST' }).catch(() => {});
    addLog(nextMute ? 'Microphone muted' : 'Microphone unmuted', 'info');
  };

  const testVoice = async () => {
    addLog('Triggering test voice command...', 'info');
    await sendCommand('Open Visual Studio Code.');
  };

  return {
    isConnected,
    agentState,
    currentTaskId,
    currentPlan,
    permissionReq,
    logs,
    systemStats,
    partialTranscript,
    isMuted,
    isListeningVoice,
    sendCommand,
    approvePermission,
    rejectPermission,
    toggleMute,
    interruptSpeaking,
    testVoice,
  };
}
