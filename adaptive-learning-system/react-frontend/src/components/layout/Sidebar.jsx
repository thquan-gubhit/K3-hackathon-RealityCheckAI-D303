import { useLang } from '../../context/LangContext';

export default function Sidebar({ units = [], activeUnitId, progress = {}, onSelectUnit, documentName }) {
  const { t, lang, setLang } = useLang();

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
    <div className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div style={{ fontSize: '1.1rem', fontWeight: 800, letterSpacing: '-0.01em' }}>
          <span className="gradient-text">Reality Check AI</span>
        </div>
        {documentName && (
          <div style={{ fontSize: '0.75rem', color: 'var(--c-text-muted)', marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            📄 {documentName}
          </div>
        )}
      </div>

      {/* Overall progress */}
      <div className="sidebar-section">
        <div className="sidebar-label">{t('sidebarProgress')}</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--c-text-muted)' }}>
            {masteredCount}/{units.length} {t('sidebarMastered')}
          </span>
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--c-primary)' }}>{pct}%</span>
        </div>
        <div className="progress-bar-wrap">
          <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* KU tree */}
      <div className="sidebar-section" style={{ flex: 1, overflowY: 'auto' }}>
        {units.map((unit, i) => {
          const status = getStatus(unit.id);
          const isActive = unit.id === activeUnitId;
          return (
            <div
              key={unit.id}
              className={`ku-tree-item${isActive ? ' active' : ''}`}
              onClick={() => onSelectUnit?.(unit.id)}
            >
              <div className={`ku-dot ${status}`} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {i + 1}. {unit.title}
              </span>
            </div>
          );
        })}
      </div>

      {/* Language toggle */}
      <div className="sidebar-section" style={{ borderTop: '1px solid var(--c-border)', paddingTop: 16 }}>
        <div className="sidebar-label">{t('language')}</div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['vi', 'en'].map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className="btn btn-ghost"
              style={{
                padding: '6px 14px',
                fontSize: '0.8rem',
                ...(lang === l ? { borderColor: 'var(--c-primary)', color: 'var(--c-primary)' } : {}),
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
