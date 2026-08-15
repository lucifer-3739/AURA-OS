import React, { useEffect, useState } from 'react';
import { Globe, Lock, ArrowRight, MousePointer, Type, RefreshCw, XCircle } from 'lucide-react';

export const BrowserMonitor: React.FC = () => {
  const [browserState, setBrowserState] = useState<Record<string, any>>({
    url: 'about:blank',
    title: 'New Tab',
    content: 'Browser session ready...',
    interactive_elements: []
  });
  const [inputUrl, setInputUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchBrowserState = async () => {
    try {
      const res = await fetch('/api/browser/state');
      const data = await res.json();
      setBrowserState(data);
      if (data.url && data.url !== 'about:blank') {
        setInputUrl(data.url);
      }
    } catch (err) {
      // ignore offline fallback
    }
  };

  useEffect(() => {
    fetchBrowserState();
    const interval = setInterval(fetchBrowserState, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleNavigate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputUrl.trim()) return;
    setLoading(true);
    try {
      await fetch('/api/browser/navigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: inputUrl }),
      });
      await fetchBrowserState();
    } finally {
      setLoading(false);
    }
  };

  const handleElementClick = async (el: any) => {
    setLoading(true);
    try {
      await fetch('/api/browser/click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selector: el.selector || el.id || '', text: el.text || '' }),
      });
      await fetchBrowserState();
    } finally {
      setLoading(false);
    }
  };

  const handleCloseBrowser = async () => {
    await fetch('/api/browser/close', { method: 'POST' });
    fetchBrowserState();
  };

  return (
    <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px', height: '100%' }}>
      {/* Browser Tab Header & URL Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)' }}>
          <Globe size={18} />
          <h3 style={{ fontSize: '14px', fontWeight: '600', fontFamily: 'var(--font-heading)' }}>
            Autonomous Browser Monitor
          </h3>
        </div>

        <form onSubmit={handleNavigate} style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
            <Lock size={12} color="var(--accent-emerald)" style={{ position: 'absolute', left: '10px' }} />
            <input
              type="text"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              placeholder="Enter web URL (e.g. https://react.dev)..."
              style={{
                width: '100%',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px 6px 28px',
                color: 'var(--text-primary)',
                fontSize: '12px',
                outline: 'none'
              }}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: 'var(--accent-cyan)',
              color: '#000',
              fontWeight: '600',
              fontSize: '11px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            Go <ArrowRight size={12} />
          </button>
        </form>

        <button
          onClick={handleCloseBrowser}
          title="Close Browser Session"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <XCircle size={18} />
        </button>
      </div>

      {/* Page Title & Status Banner */}
      <div style={{ background: 'var(--bg-secondary)', padding: '8px 12px', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)' }}>
          Tab: {browserState.title || 'New Tab'}
        </div>
        <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          {browserState.url}
        </span>
      </div>

      {/* Main Container: Page Text Content + Interactive DOM Elements */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', flex: 1, minHeight: '180px' }}>
        {/* Page Content View */}
        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: 'var(--radius-sm)', overflowY: 'auto', fontSize: '11px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
          <strong style={{ color: 'var(--accent-purple)', display: 'block', marginBottom: '4px' }}>Extracted Page Text:</strong>
          {browserState.content ? browserState.content.slice(0, 800) : 'No page content loaded.'}
        </div>

        {/* Interactive Elements List */}
        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: 'var(--radius-sm)', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <strong style={{ color: 'var(--accent-cyan)', fontSize: '11px' }}>Interactive DOM Elements:</strong>
          {(!browserState.interactive_elements || browserState.interactive_elements.length === 0) ? (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>No interactive elements detected.</span>
          ) : (
            browserState.interactive_elements.map((el: any, i: number) => (
              <div
                key={i}
                onClick={() => handleElementClick(el)}
                style={{
                  background: 'var(--bg-secondary)',
                  padding: '6px 8px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '11px',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {el.type === 'input' ? <Type size={12} color="var(--accent-purple)" /> : <MousePointer size={12} color="var(--accent-cyan)" />}
                  <span style={{ color: 'var(--text-primary)' }}>{el.text || el.placeholder || el.id || 'Element'}</span>
                </div>
                <span style={{ fontSize: '9px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{el.type}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
