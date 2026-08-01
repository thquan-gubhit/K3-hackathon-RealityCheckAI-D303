import { useState, useEffect } from 'react';
import { useLang } from '../../context/LangContext';
import { listDocuments } from '../../api/client';

export default function Sidebar({ screen, units = [], activeUnitId, progress = {}, onSelectUnit, document, onSelectDocument, onNewUpload }) {
  const { t, lang, setLang } = useLang();
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    listDocuments()
      .then((data) => {
        if (!Array.isArray(data)) return;
        const readyDocs = data.filter(d => d.status === 'ready');
        // Group by filename and keep the latest uploaded version
        const uniqueMap = new Map();
        for (const doc of readyDocs) {
          if (!uniqueMap.has(doc.filename) || new Date(doc.created_at) > new Date(uniqueMap.get(doc.filename).created_at)) {
            uniqueMap.set(doc.filename, doc);
          }
        }
        setDocs(Array.from(uniqueMap.values()).slice(0, 10));
      })
      .catch(() => {});
  }, [document]);

  const masteredCount = units.filter((u) => {
    const ku = progress[u.id] || {};
    return (ku.mastery?.mastery_score || 0) >= 0.8;
  }).length;
  const pct = units.length ? Math.round((masteredCount / units.length) * 100) : 0;

  function getStatus(unitId) {
    const ku = progress[unitId] || {};
    const score = ku.mastery?.mastery_score || 0;
    if (score >= 0.8) return 'mastered';
    if (score > 0) return 'in-progress';
    return 'not-started';
  }

  return (
    <div className="sidebar" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Logo & New Upload action */}
      <div className="sidebar-logo" style={{ paddingBottom: '12px', borderBottom: '1px solid var(--c-border)' }}>
        <div style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.01em', marginBottom: '12px' }}>
          <span className="gradient-text">Reality Check AI</span>
        </div>
        <button
          onClick={onNewUpload}
          className="btn btn-primary"
          style={{ width: '100%', padding: '8px 12px', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', borderRadius: '8px' }}
        >
          {t('sidebarUploadNew')}
        </button>
      </div>

      {/* Study Library (Uploaded documents) */}
      <div className="sidebar-section" style={{ flex: screen === 'study' ? '0 0 auto' : '1', maxHeight: screen === 'study' ? '40%' : 'none', overflowY: 'auto' }}>
        <div className="sidebar-label" style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--c-text-muted)', marginBottom: '8px' }}>
          📁 {t('sidebarDocs')}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {docs.map((docItem) => {
            const isSelected = document && docItem.filename === document.filename;
            return (
              <div
                key={docItem.id}
                onClick={() => onSelectDocument?.(docItem)}
                style={{
                  padding: '8px 10px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: isSelected ? 'rgba(124, 58, 237, 0.15)' : 'transparent',
                  color: isSelected ? '#a882ff' : 'var(--c-text)',
                  border: isSelected ? '1px solid rgba(124, 58, 237, 0.4)' : '1px solid transparent',
                  transition: 'all 0.15s ease'
                }}
              >
                <span style={{ fontSize: '1rem' }}>📄</span>
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: isSelected ? 600 : 400 }}>
                    {docItem.filename}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--c-text-muted)' }}>
                    {docItem.page_count || '?'} {lang === 'vi' ? 'trang' : 'pages'}
                  </div>
                </div>
              </div>
            );
          })}
          {docs.length === 0 && (
            <div style={{ fontSize: '0.78rem', color: 'var(--c-text-muted)', fontStyle: 'italic', padding: '4px' }}>
              {lang === 'vi' ? 'Chưa có tài liệu nào' : 'No documents yet'}
            </div>
          )}
        </div>
      </div>

      {/* Overall progress (only when a doc is active) */}
      {document && units.length > 0 && (
        <div className="sidebar-section" style={{ borderTop: '1px solid var(--c-border)', paddingTop: '14px' }}>
          <div className="sidebar-label" style={{ marginBottom: '8px' }}>{t('sidebarProgress')}</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--c-text-muted)' }}>
              {masteredCount}/{units.length} {t('sidebarMastered')}
            </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--c-primary)' }}>{pct}%</span>
          </div>
          <div className="progress-bar-wrap" style={{ height: '6px' }}>
            <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}

      {/* KU tree — exclusively shown in Study Room to avoid redundancy in Dashboard */}
      {screen === 'study' && units.length > 0 && (
        <div className="sidebar-section" style={{ flex: 1, overflowY: 'auto', borderTop: '1px solid var(--c-border)', paddingTop: '14px' }}>
          <div className="sidebar-label" style={{ marginBottom: '8px' }}>🎯 {t('sidebarTopics')}</div>
          {units.map((unit, i) => {
            const status = getStatus(unit.id);
            const isActive = unit.id === activeUnitId;
            return (
              <div
                key={unit.id}
                className={`ku-tree-item${isActive ? ' active' : ''}`}
                onClick={() => onSelectUnit?.(unit.id)}
                style={{ padding: '6px 8px', margin: '2px 0', borderRadius: '6px', fontSize: '0.82rem' }}
              >
                <div className={`ku-dot ${status}`} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
                  {i + 1}. {unit.title}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Language toggle */}
      <div className="sidebar-section" style={{ borderTop: '1px solid var(--c-border)', paddingTop: '14px', marginTop: 'auto' }}>
        <div className="sidebar-label" style={{ marginBottom: '8px' }}>🌐 {t('language')}</div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['vi', 'en'].map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className="btn btn-ghost"
              style={{
                flex: 1,
                padding: '6px 0',
                fontSize: '0.8rem',
                fontWeight: lang === l ? 700 : 400,
                ...(lang === l ? { borderColor: 'var(--c-primary)', color: 'var(--c-primary)', backgroundColor: 'rgba(124, 58, 237, 0.1)' } : {}),
              }}
            >
              {l === 'vi' ? '🇻🇳 Tiếng Việt' : '🇺🇸 English'}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
