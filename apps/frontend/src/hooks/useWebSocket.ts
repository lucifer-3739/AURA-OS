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

export function useWebSocket(url: string = 'ws://127.0.0.1:8000/api/ws') {
  const [isConnected, setIsConnected] = useState(false);
  const [agentState, setAgentState] = useState<string>('IDLE');
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentPlan, setCurrentPlan] = useState<PlanStep[]>([]);
  const [permissionReq, setPermissionReq] = useState<PermissionRequest | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [systemStats, setSystemStats] = useState<Record<string, any>>({});

  // Voice State (Phase 2)
  const [partialTranscript, setPartialTranscript] = useState<string>('');
  const [isMuted, setIsMuted] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);

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

  useEffect(() => {
    let socket: WebSocket;

    const connect = () => {
      socket = new WebSocket(url);
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
              if (state === 'IDLE' || state === 'COMPLETED' || state === 'FAILED' || state === 'CANCELLED') {
                setPermissionReq(null);
                setPartialTranscript('');
              }
              break;

            case 'wake_word_detected':
              addLog('Wake word "Hey Aura" detected! Listening for user command...', 'success');
              break;

            case 'speech_partial':
              if (data?.text) setPartialTranscript(data.text);
              break;

            case 'speech_final':
              if (data?.text) {
                setPartialTranscript(data.text);
                addLog(`Voice Recognized: "${data.text}"`, 'info');
              }
              break;

            case 'ai_response_started':
              if (data?.text) {
                addLog(`AURA TTS Output: "${data.text}"`, 'info');
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
        addLog('Disconnected from AURA OS Engine. Retrying...', 'warn');
        setTimeout(connect, 3000);
      };

      socket.onerror = (err) => {
        console.error('WebSocket Error:', err);
      };
    };

    connect();

    return () => {
      if (socket) socket.close();
    };
  }, [url, addLog]);

  const sendCommand = async (command: string) => {
    try {
      addLog(`User command: "${command}"`, 'info');
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      return await res.json();
    } catch (err: any) {
      addLog(`Failed to send command: ${err.message}`, 'error');
    }
  };

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
    const endpoint = nextMute ? '/api/voice/mute' : '/api/voice/unmute';
    await fetch(endpoint, { method: 'POST' });
    addLog(nextMute ? 'Microphone muted' : 'Microphone unmuted', 'info');
  };

  const interruptSpeaking = async () => {
    await fetch('/api/voice/interrupt', { method: 'POST' });
    addLog('Interrupted TTS speech playback', 'warn');
  };

  const testVoice = async () => {
    addLog('Triggered simulated voice pipeline test run...', 'info');
    await fetch('/api/voice/test', { method: 'POST' });
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
    sendCommand,
    approvePermission,
    rejectPermission,
    toggleMute,
    interruptSpeaking,
    testVoice,
  };
}
