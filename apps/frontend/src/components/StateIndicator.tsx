import React from 'react';
import { Activity, ShieldAlert, CheckCircle2, XCircle, Clock, Zap } from 'lucide-react';

interface StateIndicatorProps {
  state: string;
  isConnected: boolean;
}

export const StateIndicator: React.FC<StateIndicatorProps> = ({ state, isConnected }) => {
  const getStateColor = (st: string) => {
    switch (st) {
      case 'IDLE': return '#64748b';
      case 'WAITING_FOR_WAKE_WORD': return '#00e5ff';
      case 'WAKE_WORD_DETECTED':
      case 'LISTENING': return '#10b981';
      case 'PROCESSING_SPEECH':
      case 'UNDERSTANDING':
      case 'PLANNING':
      case 'THINKING': return '#3b82f6';
      case 'WAITING_FOR_PERMISSION': return '#f59e0b';
      case 'EXECUTING':
      case 'OBSERVING':
      case 'VERIFYING': return '#8b5cf6';
      case 'SPEAKING': return '#ec4899';
      case 'INTERRUPTED': return '#f59e0b';
      case 'COMPLETED': return '#10b981';
      case 'FAILED':
      case 'CANCELLED':
      case 'ERROR': return '#f43f5e';
      default: return '#00e5ff';
    }
  };

  const color = getStateColor(state);

  return (
    <div className="glass-panel" style={{ padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div 
          style={{ 
            width: '14px', 
            height: '14px', 
            borderRadius: '50%', 
            backgroundColor: color,
            boxShadow: `0 0 16px ${color}`,
            transition: 'all 0.3s ease'
          }} 
        />
        <div>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)' }}>
            Agent State Machine
          </div>
          <div style={{ fontSize: '18px', fontWeight: '700', fontFamily: 'var(--font-heading)', color: 'var(--text-primary)', marginTop: '2px' }}>
            {state}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ fontSize: '12px', color: isConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: isConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)' }} />
          {isConnected ? 'Engine Online' : 'Engine Disconnected'}
        </div>
      </div>
    </div>
  );
};
