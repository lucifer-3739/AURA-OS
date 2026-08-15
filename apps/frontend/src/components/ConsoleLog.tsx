import React from 'react';
import { LogEntry } from '../hooks/useWebSocket';
import { Terminal } from 'lucide-react';

interface ConsoleLogProps {
  logs: LogEntry[];
}

export const ConsoleLog: React.FC<ConsoleLogProps> = ({ logs }) => {
  return (
    <div className="glass-panel" style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <Terminal size={16} color="var(--accent-cyan)" />
        <h3 style={{ fontSize: '14px', fontWeight: '600', fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
          Audit & Tool Activity Stream
        </h3>
      </div>

      <div 
        style={{ 
          flex: 1, 
          background: 'rgba(0, 0, 0, 0.4)', 
          borderRadius: 'var(--radius-sm)', 
          padding: '12px', 
          fontFamily: 'var(--font-mono)', 
          fontSize: '12px', 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }}
      >
        {logs.length === 0 ? (
          <span style={{ color: 'var(--text-muted)' }}>Console ready. Logs will appear here...</span>
        ) : (
          logs.map((log) => {
            const getColor = (t: string) => {
              switch (t) {
                case 'success': return 'var(--accent-emerald)';
                case 'warn': return 'var(--accent-amber)';
                case 'error': return 'var(--accent-rose)';
                default: return 'var(--text-secondary)';
              }
            };

            return (
              <div key={log.id} style={{ display: 'flex', gap: '8px', lineHeight: '1.4' }}>
                <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>[{log.timestamp}]</span>
                <span style={{ color: getColor(log.type) }}>{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
