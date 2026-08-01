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

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: 8 }}>
          <span className="gradient-text">{t('pathTitle')}</span>
        </h1>
        <p style={{ color: 'var(--c-text-muted)' }}>{t('pathSubtitle')}</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.82rem', color: 'var(--c-text-muted)' }}>
              <span>{masteredCount}/{units.length} {t('sidebarMastered')}</span>
              <span style={{ color: 'var(--c-primary)', fontWeight: 700 }}>{overallPct}%</span>
            </div>
            <div className="progress-bar-wrap">
              <div className="progress-bar-fill" style={{ width: `${overallPct}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* KU Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 18 }}>
        {units.map((unit, i) => {
          const status = getStatus(unit.id);
          const score = getUnitMastery(unit.id);
          const pct = Math.round(score * 100);
          const isMastered = status === 'mastered';
          const isInProgress = status === 'in-progress';
          const isLoading = loading === unit.id;

          return (
            <div key={unit.id} className={`ku-card${isMastered ? ' mastered' : ''}`}>
              <div>
                <div className="ku-card-number">
                  Topic {i + 1} / {units.length}
                </div>
                <div className="ku-card-title">{unit.title}</div>
              </div>

              {/* Status badge */}
              <div>
                <span className={`ku-status-badge ${status === 'mastered' ? 'mastered-status' : status}`}>
                  {status === 'mastered' && '✅ '}
                  {status === 'in-progress' && '🔄 '}
                  {status === 'not-started' && '○ '}
                  {t(status === 'mastered' ? 'unitMastered' : status === 'in-progress' ? 'unitInProgress' : 'unitNotStarted')}
                </span>
              </div>

              {/* Progress bar */}
              {score > 0 && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--c-text-muted)', marginBottom: 5 }}>
                    <span>{t('masteryLabel')}</span>
                    <span style={{ fontWeight: 700, color: isMastered ? 'var(--c-success)' : 'var(--c-primary)' }}>{pct}%</span>
                  </div>
                  <div className="progress-bar-wrap">
                    <div className="progress-bar-fill" style={{ width: `${pct}%`, background: isMastered ? 'linear-gradient(90deg,#16A34A,#22C55E)' : undefined }} />
                  </div>
                </div>
              )}

              {/* CTA */}
              <button
                className={`btn ${isMastered ? 'btn-ghost' : 'btn-primary'}`}
                style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => handleStart(unit)}
                disabled={isLoading}
              >
                {isLoading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Loading...</>
                  : isMastered ? t('btnReview')
                  : isInProgress ? t('btnContinue')
                  : t('btnStart')}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
