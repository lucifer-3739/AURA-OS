import React from 'react';
import { PermissionRequest } from '../hooks/useWebSocket';
import { ShieldAlert, Check, X } from 'lucide-react';

interface PermissionPromptProps {
  request: PermissionRequest | null;
  onApprove: () => void;
  onReject: () => void;
}

export const PermissionPrompt: React.FC<PermissionPromptProps> = ({ request, onApprove, onReject }) => {
  if (!request) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
    >
      <div 
        className="glass-panel" 
        style={{
          width: '100%',
          maxWidth: '460px',
          padding: '24px',
          border: '1px solid var(--accent-amber)',
          boxShadow: '0 0 40px rgba(245, 158, 11, 0.25)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <ShieldAlert size={28} color="var(--accent-amber)" />
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
              Security Permission Required
            </h3>
            <span style={{ fontSize: '12px', color: 'var(--accent-amber)', fontWeight: '600' }}>
              Risk Level: {request.risk_level}
            </span>
          </div>
        </div>

        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: '1.5' }}>
          The AI agent requests permission to execute the following sensitive action:
        </p>

        <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: 'var(--radius-sm)', marginBottom: '20px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
          <div><strong style={{ color: 'var(--text-primary)' }}>Tool:</strong> {request.tool_name}</div>
          <div style={{ marginTop: '4px', color: 'var(--text-muted)' }}>
            <strong>Arguments:</strong> {JSON.stringify(request.arguments)}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onApprove}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: 'var(--accent-emerald)',
              color: '#fff',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <Check size={16} /> Approve Execution
          </button>

          <button
            onClick={onReject}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color)',
              background: 'transparent',
              color: 'var(--text-primary)',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <X size={16} /> Reject
          </button>
        </div>
      </div>
    </div>
  );
};
