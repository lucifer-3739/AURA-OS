import React, { useEffect, useState } from 'react';
import { Cpu, HardDrive, ShieldCheck } from 'lucide-react';

export const SystemStats: React.FC = () => {
  const [stats, setStats] = useState<Record<string, any>>({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.system) {
          setStats(data.system);
        }
      } catch (err) {
        // ignore fallback
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ fontSize: '13px', fontWeight: '600', fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>
        System Hardware & Diagnostics
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '11px' }}>
            <Cpu size={14} color="var(--accent-cyan)" /> CPU Load
          </div>
          <div style={{ fontSize: '16px', fontWeight: '700', marginTop: '4px', color: 'var(--accent-cyan)' }}>
            {stats.cpu_percent ?? 0}%
          </div>
        </div>

        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '11px' }}>
            <HardDrive size={14} color="var(--accent-purple)" /> RAM Used
          </div>
          <div style={{ fontSize: '16px', fontWeight: '700', marginTop: '4px', color: 'var(--accent-purple)' }}>
            {stats.ram_percent ?? 0}%
          </div>
        </div>

        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '11px' }}>
            <ShieldCheck size={14} color="var(--accent-emerald)" /> Security
          </div>
          <div style={{ fontSize: '14px', fontWeight: '600', marginTop: '4px', color: 'var(--accent-emerald)' }}>
            Active (Interactive)
          </div>
        </div>
      </div>
    </div>
  );
};
