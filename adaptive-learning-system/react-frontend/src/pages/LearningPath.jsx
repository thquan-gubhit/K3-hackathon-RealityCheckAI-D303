import { useLang } from '../context/LangContext';
import { createLearningSession, getUserProgress } from '../api/client';
import { useState, useEffect } from 'react';

export default function LearningPath({ document, units, onStartUnit }) {
  const { t } = useLang();
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(null); // unitId being loaded

  useEffect(() => {
    getUserProgress()
      .then((data) => {
        const map = {};
        for (const ku of data.knowledge_units || []) {
          map[ku.knowledge_unit_id] = ku;
        }
        setProgress(map);
      })
      .catch(() => {});
  }, []);

  function getUnitMastery(unitId) {
    const ku = progress[unitId] || {};
    return ku.mastery?.mastery_score || 0;
  }

  function getStatus(unitId) {
    const score = getUnitMastery(unitId);
    if (score >= 0.8) return 'mastered';
    if (score > 0) return 'in-progress';
    return 'not-started';
  }

  async function handleStart(unit) {
    setLoading(unit.id);
    try {
      const session = await createLearningSession(document.id, unit.id);
      onStartUnit(unit, session);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(null);
    }
  }

  const masteredCount = units.filter((u) => getStatus(u.id) === 'mastered').length;
  const overallPct = units.length ? Math.round((masteredCount / units.length) * 100) : 0;

  // Find index of the very first topic that is NOT mastered yet to recommend as next step
  const nextTargetIdx = units.findIndex((u) => getStatus(u.id) !== 'mastered');

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: '2.1rem', fontWeight: 800, marginBottom: 8 }}>
          <span className="gradient-text">{t('pathTitle')}</span>
        </h1>
        <p style={{ color: 'var(--c-text-muted)', fontSize: '0.95rem' }}>{t('pathSubtitle')}</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 18, background: 'var(--c-surface-card)', padding: '16px', borderRadius: '12px', border: '1px solid var(--c-border)' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.88rem', color: 'var(--c-text-muted)', fontWeight: 600 }}>
              <span>🏆 {masteredCount}/{units.length} {t('sidebarMastered')}</span>
              <span style={{ color: 'var(--c-primary)', fontWeight: 700 }}>{overallPct}%</span>
            </div>
            <div className="progress-bar-wrap" style={{ height: '8px' }}>
              <div className="progress-bar-fill" style={{ width: `${overallPct}%`, background: 'linear-gradient(90deg, var(--c-primary), #a78bfa)' }} />
            </div>
          </div>
        </div>
      </div>

      {/* KU Cards Grid with Sequential Journey Highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '22px' }}>
        {units.map((unit, i) => {
          const status = getStatus(unit.id);
          const score = getUnitMastery(unit.id);
          const pct = Math.round(score * 100);
          const isMastered = status === 'mastered';
          const isInProgress = status === 'in-progress';
          const isLoading = loading === unit.id;
          const isRecommended = (i === nextTargetIdx || (nextTargetIdx === -1 && i === units.length - 1));

          return (
            <div
              key={unit.id}
              className={`ku-card${isMastered ? ' mastered' : ''}`}
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                border: isRecommended ? '2px solid var(--c-primary)' : isMastered ? '1px solid #16A34A' : '1px solid var(--c-border)',
                boxShadow: isRecommended ? '0 0 20px rgba(124, 58, 237, 0.25)' : 'none',
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
                backgroundColor: isRecommended ? 'rgba(124, 58, 237, 0.05)' : 'var(--c-surface-card)'
              }}
            >
              {/* Recommended Top Ribbon */}
              {isRecommended && !isMastered && (
                <div style={{
                  backgroundColor: 'var(--c-primary)',
                  color: '#fff',
                  fontSize: '0.72rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  padding: '4px 12px',
                  borderRadius: '0 0 8px 8px',
                  alignSelf: 'flex-start',
                  marginBottom: '12px',
                  boxShadow: '0 2px 8px rgba(124, 58, 237, 0.4)'
                }}>
                  {t('recommendedNext')}
                </div>
              )}

              <div>
                <div className="ku-card-number" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>Topic {i + 1} / {units.length}</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-text-muted)' }}>
                    {t('stepNumber').replace('{n}', i + 1)}
                  </span>
                </div>
                <div className="ku-card-title" style={{ fontSize: '1.15rem', marginTop: '6px', marginBottom: '14px' }}>
                  {unit.title}
                </div>
              </div>

              {/* Status & Progress section */}
              <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px dashed var(--c-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span className={`ku-status-badge ${status === 'mastered' ? 'mastered-status' : status}`} style={{ margin: 0 }}>
                    {status === 'mastered' && '✅ '}
                    {status === 'in-progress' && '🔄 '}
                    {status === 'not-started' && '○ '}
                    {t(status === 'mastered' ? 'unitMastered' : status === 'in-progress' ? 'unitInProgress' : 'unitNotStarted')}
                  </span>

                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: isMastered ? '#22c55e' : score > 0 ? 'var(--c-primary)' : 'var(--c-text-muted)' }}>
                    {pct}% {t('masteryLabel')}
                  </span>
                </div>

                <div className="progress-bar-wrap" style={{ marginBottom: '16px', height: '6px' }}>
                  <div className="progress-bar-fill" style={{ width: `${pct}%`, background: isMastered ? 'linear-gradient(90deg,#16A34A,#22C55E)' : 'linear-gradient(90deg, var(--c-primary), #a882ff)' }} />
                </div>

                {/* Action button */}
                <button
                  className={`btn ${isRecommended ? 'btn-primary' : isMastered ? 'btn-ghost' : 'btn-ghost'}`}
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    padding: '10px',
                    fontWeight: isRecommended ? 700 : 600,
                    border: isMastered || !isRecommended ? '1px solid var(--c-border)' : 'none',
                    backgroundColor: isRecommended ? 'var(--c-primary)' : 'transparent'
                  }}
                  onClick={() => handleStart(unit)}
                  disabled={isLoading}
                >
                  {isLoading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Loading...</>
                    : isMastered ? t('btnReview')
                    : isInProgress ? t('btnContinue')
                    : t('btnStart')}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
