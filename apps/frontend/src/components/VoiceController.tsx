import React, { useState, useEffect } from 'react';
import { Mic, MicOff, VolumeX, Radio, Sparkles, Play, ShieldCheck } from 'lucide-react';

interface VoiceControllerProps {
  agentState: string;
  partialTranscript: string;
  isMuted: boolean;
  isListeningVoice?: boolean;
  micPermissionGranted?: boolean;
  micVolume?: number;
  onRequestMicAccess: () => void;
  onToggleMute: () => void;
  onInterrupt: () => void;
  onTestVoice: () => void;
}

export const VoiceController: React.FC<VoiceControllerProps> = ({
  agentState,
  partialTranscript,
  isMuted,
  isListeningVoice = false,
  micPermissionGranted = false,
  micVolume = 0,
  onRequestMicAccess,
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
    }).catch(() => {});
  };

  const getOrbColor = () => {
    if (isMuted) return 'rgba(244, 63, 94, 0.4)';
    if (isListeningVoice) return 'rgba(16, 185, 129, 0.9)';
    switch (agentState) {
      case 'WAITING_FOR_WAKE_WORD': return 'rgba(0, 229, 255, 0.4)';
      case 'WAKE_WORD_DETECTED':
      case 'LISTENING': return 'rgba(16, 185, 129, 0.8)';
      case 'PROCESSING_SPEECH':
      case 'THINKING': return 'rgba(139, 92, 246, 0.8)';
      case 'SPEAKING': return 'rgba(236, 72, 153, 0.8)';
      case 'INTERRUPTED': return 'rgba(245, 158, 11, 0.8)';
      case 'ERROR': return 'rgba(244, 63, 94, 0.8)';
      default: return 'rgba(0, 229, 255, 0.5)';
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Radio size={18} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '15px', fontWeight: '600', fontFamily: 'var(--font-heading)' }}>
            Live Voice Controller
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
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '12px 0' }}>
        <div
          onClick={onRequestMicAccess}
          title="Click to Grant/Check Microphone Permission"
          style={{
            width: '76px',
            height: '76px',
            borderRadius: '50%',
            background: `radial-gradient(circle, ${getOrbColor()} 0%, transparent 75%)`,
            boxShadow: `0 0 35px ${getOrbColor()}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          {isMuted ? <MicOff size={28} color="var(--accent-rose)" /> : <Mic size={28} color="#fff" />}
        </div>

        {/* Microphone Volume Meter Bar */}
        <div style={{ width: '100%', maxWidth: '200px', height: '4px', background: 'var(--bg-secondary)', borderRadius: '2px', marginTop: '12px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${micVolume}%`,
              height: '100%',
              background: micVolume > 50 ? 'var(--accent-emerald)' : 'var(--accent-cyan)',
              transition: 'width 0.1s ease'
            }}
          />
        </div>

        <div style={{ marginTop: '8px', textAlign: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Status:{' '}
            <strong style={{ color: isMuted ? 'var(--accent-rose)' : micPermissionGranted ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
              {isMuted ? 'Mic Muted' : micPermissionGranted ? 'Mic Active & Listening...' : 'Click Orb to Grant Mic Access'}
            </strong>
          </span>
          {partialTranscript && (
            <div style={{ marginTop: '8px', fontSize: '13px', fontWeight: '500', color: 'var(--accent-cyan)', fontStyle: 'italic' }}>
              "{partialTranscript}"
            </div>
          )}
        </div>
      </div>

      {/* Voice Control Buttons */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={onRequestMicAccess}
          style={{
            flex: 1,
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-glow)',
            background: micPermissionGranted ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.2)',
            color: micPermissionGranted ? 'var(--accent-emerald)' : 'var(--accent-amber)',
            fontSize: '11px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '4px'
          }}
        >
          <ShieldCheck size={14} /> {micPermissionGranted ? 'Mic Granted' : 'Enable Mic'}
        </button>

        <button
          onClick={onToggleMute}
          style={{
            flex: 1,
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-color)',
            background: isMuted ? 'rgba(244, 63, 94, 0.15)' : 'var(--bg-secondary)',
            color: isMuted ? 'var(--accent-rose)' : 'var(--text-primary)',
            fontSize: '11px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '4px'
          }}
        >
          {isMuted ? <MicOff size={14} /> : <Mic size={14} />}
          {isMuted ? 'Unmute' : 'Mute'}
        </button>

        <button
          onClick={onInterrupt}
          style={{
            flex: 1,
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            background: 'rgba(244, 63, 94, 0.2)',
            color: 'var(--accent-rose)',
            fontSize: '11px',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '4px'
          }}
        >
          <VolumeX size={14} /> STOP ALL
        </button>

        <button
          onClick={onTestVoice}
          style={{
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-glow)',
            background: 'rgba(0, 229, 255, 0.1)',
            color: 'var(--accent-cyan)',
            fontSize: '11px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <Play size={14} /> Test
        </button>
      </div>
    </div>
  );
};
