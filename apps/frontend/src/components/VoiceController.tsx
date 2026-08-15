import React, { useState, useEffect } from 'react';
import { Mic, MicOff, VolumeX, Radio, Sparkles, Settings2, Play } from 'lucide-react';

interface VoiceControllerProps {
  agentState: string;
  partialTranscript: string;
  isMuted: boolean;
  onToggleMute: () => void;
  onInterrupt: () => void;
  onTestVoice: () => void;
}

export const VoiceController: React.FC<VoiceControllerProps> = ({
  agentState,
  partialTranscript,
  isMuted,
  onToggleMute,
  onInterrupt,
  onTestVoice,
}) => {
  const [devices, setDevices] = useState<any[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('default');

  useEffect(() => {
    fetch('/api/audio/devices')
      .then((res) => res.json())
      .then((data) => {
        if (data.devices) setDevices(data.devices);
        if (data.selected_device) setSelectedDevice(data.selected_device);
      })
      .catch(() => {});
  }, []);

  const handleDeviceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const devId = e.target.value;
    setSelectedDevice(devId);
    fetch('/api/audio/devices/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: devId }),
    });
  };

  const getOrbColor = () => {
    switch (agentState) {
      case 'WAITING_FOR_WAKE_WORD': return 'rgba(0, 229, 255, 0.4)';
      case 'WAKE_WORD_DETECTED':
      case 'LISTENING': return 'rgba(16, 185, 129, 0.8)';
      case 'PROCESSING_SPEECH':
      case 'THINKING': return 'rgba(139, 92, 246, 0.8)';
      case 'SPEAKING': return 'rgba(236, 72, 153, 0.8)';
      case 'INTERRUPTED': return 'rgba(245, 158, 11, 0.8)';
      case 'ERROR': return 'rgba(244, 63, 94, 0.8)';
      default: return 'rgba(100, 116, 139, 0.4)';
    }
  };

  const isSpeaking = agentState === 'SPEAKING';

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Radio size={18} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '15px', fontWeight: '600', fontFamily: 'var(--font-heading)' }}>
            Voice Control Pipeline
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <select
            value={selectedDevice}
            onChange={handleDeviceChange}
            style={{
              background: 'var(--bg-secondary)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: '4px 8px',
              fontSize: '11px',
              outline: 'none'
            }}
          >
            {devices.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Center Voice Orb Visualizer */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '16px 0' }}>
        <div
          style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            background: `radial-gradient(circle, ${getOrbColor()} 0%, transparent 70%)`,
            boxShadow: `0 0 35px ${getOrbColor()}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease'
          }}
        >
          <Sparkles size={28} color="#fff" />
        </div>

        <div style={{ marginTop: '12px', textAlign: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Wake Word: <strong style={{ color: 'var(--accent-cyan)' }}>"Hey Aura"</strong>
          </span>
          {partialTranscript && (
            <div style={{ marginTop: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--accent-cyan)', fontStyle: 'italic' }}>
              "{partialTranscript}"
            </div>
          )}
        </div>
      </div>

      {/* Voice Control Buttons */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={onToggleMute}
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-color)',
            background: isMuted ? 'rgba(244, 63, 94, 0.15)' : 'var(--bg-secondary)',
            color: isMuted ? 'var(--accent-rose)' : 'var(--text-primary)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}
        >
          {isMuted ? <MicOff size={14} /> : <Mic size={14} />}
          {isMuted ? 'Mic Muted' : 'Mute Mic'}
        </button>

        <button
          onClick={onInterrupt}
          disabled={!isSpeaking}
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-color)',
            background: isSpeaking ? 'rgba(245, 158, 11, 0.2)' : 'var(--bg-secondary)',
            color: isSpeaking ? 'var(--accent-amber)' : 'var(--text-muted)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: isSpeaking ? 'pointer' : 'default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}
        >
          <VolumeX size={14} /> Stop Speech
        </button>

        <button
          onClick={onTestVoice}
          style={{
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-glow)',
            background: 'rgba(0, 229, 255, 0.1)',
            color: 'var(--accent-cyan)',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Play size={14} /> Test Voice
        </button>
      </div>
    </div>
  );
};
