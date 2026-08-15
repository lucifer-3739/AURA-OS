import React from 'react';
import { PlanStep } from '../hooks/useWebSocket';
import { CheckCircle2, Circle, Loader2, AlertCircle, Shield } from 'lucide-react';

interface TaskMonitorProps {
  plan: PlanStep[];
  currentTaskId: string | null;
}

export const TaskMonitor: React.FC<TaskMonitorProps> = ({ plan, currentTaskId }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: '600', fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
          Active Task Execution Plan
        </h3>
        {currentTaskId && (
          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', background: 'var(--bg-secondary)', padding: '4px 8px', borderRadius: '4px' }}>
            ID: {currentTaskId.slice(0, 8)}...
          </span>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {plan.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '40px 0' }}>
            No active plan. Type a command to start.
          </div>
        ) : (
          plan.map((step) => {
            const isCompleted = step.status === 'completed';
            const isExecuting = step.status === 'executing';
            const isWaiting = step.status === 'waiting_for_permission';
            const isFailed = step.status === 'failed';

            return (
              <div
                key={step.id}
                style={{
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: isExecuting ? 'rgba(0, 229, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: isExecuting ? '1px solid var(--border-glow)' : '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}
              >
                <div style={{ marginTop: '2px' }}>
                  {isCompleted && <CheckCircle2 size={18} color="var(--accent-emerald)" />}
                  {isExecuting && <Loader2 size={18} color="var(--accent-cyan)" className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />}
                  {isWaiting && <Shield size={18} color="var(--accent-amber)" />}
                  {isFailed && <AlertCircle size={18} color="var(--accent-rose)" />}
                  {!isCompleted && !isExecuting && !isWaiting && !isFailed && <Circle size={18} color="var(--text-muted)" />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: '500', color: isCompleted ? 'var(--text-secondary)' : 'var(--text-primary)' }}>
                    {step.description}
                  </div>
                  <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Tool: <span style={{ color: 'var(--accent-cyan)' }}>{step.tool_name}</span>
                  </div>
                  {step.error && (
                    <div style={{ fontSize: '11px', color: 'var(--accent-rose)', marginTop: '4px' }}>
                      Error: {step.error}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
