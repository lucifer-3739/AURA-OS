import React, { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { StateIndicator } from './components/StateIndicator';
import { TaskMonitor } from './components/TaskMonitor';
import { ConsoleLog } from './components/ConsoleLog';
import { PermissionPrompt } from './components/PermissionPrompt';
import { SystemStats } from './components/SystemStats';
import { VoiceController } from './components/VoiceController';
import { Send, Mic, Sparkles, FolderPlus, Search, Command, Shield } from 'lucide-react';

export const App: React.FC = () => {
  const [inputCommand, setInputCommand] = useState('');

  const {
    isConnected,
    agentState,
    currentTaskId,
    currentPlan,
    permissionReq,
    logs,
    partialTranscript,
    isMuted,
    sendCommand,
    approvePermission,
    rejectPermission,
    toggleMute,
    interruptSpeaking,
    testVoice,
  } = useWebSocket();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputCommand.trim()) return;
    const cmd = inputCommand;
    setInputCommand('');
    await sendCommand(cmd);
  };

  const handleSuggestion = async (cmd: string) => {
    setInputCommand('');
    await sendCommand(cmd);
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', width: '100%', flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div 
            style={{ 
              width: '38px', 
              height: '38px', 
              borderRadius: '10px', 
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow-cyan)'
            }}
          >
            <Sparkles size={20} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: '800', fontFamily: 'var(--font-heading)', letterSpacing: '-0.5px' }}>
              AURA OS
            </h1>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              AI-Native Voice-Controlled Computer Agent • Phase 2
            </span>
          </div>
        </div>

        <SystemStats />
      </div>

      {/* Top Agent State Machine Bar */}
      <StateIndicator state={agentState} isConnected={isConnected} />

      {/* Voice Control & Quick Suggestion Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        <VoiceController
          agentState={agentState}
          partialTranscript={partialTranscript}
          isMuted={isMuted}
          onToggleMute={toggleMute}
          onInterrupt={interruptSpeaking}
          onTestVoice={testVoice}
        />

        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: '600', fontFamily: 'var(--font-heading)', marginBottom: '10px' }}>
              Quick Action Prompts
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Say <strong>"Hey Aura"</strong> or click any suggestion below to issue commands via text or voice pipeline.
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button onClick={() => handleSuggestion('Open VS Code.')} style={pillStyle}>
                <Command size={14} color="var(--accent-cyan)" /> "Open VS Code"
              </button>
              <button onClick={() => handleSuggestion('Create a folder called Projects.')} style={pillStyle}>
                <FolderPlus size={14} color="var(--accent-purple)" /> "Create Projects Folder"
              </button>
              <button onClick={() => handleSuggestion('Search the web for React documentation.')} style={pillStyle}>
                <Search size={14} color="var(--accent-emerald)" /> "Search React Docs"
              </button>
              <button onClick={() => handleSuggestion('Delete folder Projects_Test.')} style={pillStyle}>
                <Shield size={14} color="var(--accent-amber)" /> "Test Dangerous Permission"
              </button>
            </div>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: 'var(--radius-sm)', fontSize: '11px', color: 'var(--text-muted)' }}>
            <strong>Interruption Commands:</strong> Say "Stop talking" / "Cancel task" to halt speech or abort execution instantly. Say "Yes" / "No" to handle security permission requests.
          </div>
        </div>
      </div>

      {/* Main Grid: Task Progress Monitor + Console Audit Logs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', flex: 1, minHeight: '340px' }}>
        <TaskMonitor plan={currentPlan} currentTaskId={currentTaskId} />
        <ConsoleLog logs={logs} />
      </div>

      {/* Command Input Area */}
      <div className="glass-panel" style={{ padding: '12px 16px' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ color: 'var(--accent-cyan)', paddingLeft: '4px' }}>
            <Mic size={20} />
          </div>

          <input
            type="text"
            value={inputCommand}
            onChange={(e) => setInputCommand(e.target.value)}
            placeholder='Say "Hey Aura..." or type a natural language command here...'
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-body)',
              fontSize: '15px'
            }}
          />

          <button
            type="submit"
            disabled={!inputCommand.trim()}
            style={{
              padding: '10px 20px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: inputCommand.trim() ? 'var(--accent-cyan)' : 'var(--bg-secondary)',
              color: inputCommand.trim() ? '#000' : 'var(--text-muted)',
              fontWeight: '600',
              cursor: inputCommand.trim() ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            Execute <Send size={16} />
          </button>
        </form>
      </div>

      {/* Interactive Permission Interruption Prompt Modal */}
      <PermissionPrompt
        request={permissionReq}
        onApprove={approvePermission}
        onReject={rejectPermission}
      />
    </div>
  );
};

const pillStyle: React.CSSProperties = {
  background: 'var(--bg-card)',
  border: '1px solid var(--border-color)',
  borderRadius: '20px',
  padding: '6px 14px',
  color: 'var(--text-secondary)',
  fontSize: '12px',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  transition: 'all 0.2s ease'
};

export default App;
