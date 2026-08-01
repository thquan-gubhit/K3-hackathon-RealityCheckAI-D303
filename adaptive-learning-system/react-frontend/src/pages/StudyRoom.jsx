import { useState, useEffect } from 'react';
import { useLang } from '../context/LangContext';
import { getNextQuestion, submitAnswer } from '../api/client';

// ── Score Pill ────────────────────────────────────────────────────
function ScorePill({ label, score }) {
  const pct = Math.round(score * 100);
  const color = pct >= 80 ? 'var(--c-success)' : pct >= 50 ? 'var(--c-warning)' : 'var(--c-danger)';
  return (
    <div className="score-pill">
      <span className="value" style={{ color }}>{pct}%</span>
      <span className="label">{label}</span>
    </div>
  );
}

// ── Feedback Card ──────────────────────────────────────────────────
function FeedbackCard({ type, label, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className={`feedback-card ${type}`}>
      <div className="card-label">{label}</div>
      <ul style={{ paddingLeft: 16 }}>
        {items.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </div>
  );
}

// ── Main Study Room ──────────────────────────────────────────────────
export default function StudyRoom({ document: doc, unit, session, onBack }) {
  const { t, fmt } = useLang();
  const [phase, setPhase] = useState('reading'); // reading | loading | recall | evaluated | tutor | done
  const [nextData, setNextData] = useState(null); // { session, question, route_reason, next_action }
  const [answer, setAnswer] = useState('');
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [refExpanded, setRefExpanded] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [startTime] = useState(Date.now());
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const pages = (unit.source_pages && unit.source_pages.length > 0) ? unit.source_pages : [1];
  const currentPage = pages[currentSlideIndex] || pages[0];
  const docId = doc?.id || unit?.document_id;

  useEffect(() => {
    setCurrentSlideIndex(0);
  }, [unit.id]);

  async function loadNextQuestion(sessionId) {
    setPhase('loading');
    setAnswer('');
    setResult(null);
    setRefExpanded(false);
    try {
      const data = await getNextQuestion(sessionId);
      setNextData(data);
      if (!data.question || data.next_action === 'UNIT_COMPLETE') {
        setPhase('done');
      } else {
        setPhase('recall');
      }
    } catch (e) {
      alert(e.message);
    }
  }

  // Preload first question in background while user reads slide content
  useEffect(() => {
    getNextQuestion(session.id)
      .then((data) => setNextData(data))
      .catch(() => {});
  }, [session.id]);

  function handleStartTesting() {
    if (!nextData) {
      loadNextQuestion(session.id);
    } else if (result !== null) {
      setPhase('evaluated');
    } else if (!nextData.question || nextData.next_action === 'UNIT_COMPLETE') {
      setPhase('done');
    } else {
      setPhase('recall');
    }
  }

  async function handleSubmit() {
    if (!answer.trim() || !nextData?.question) return;
    setSubmitting(true);
    try {
      const res = await submitAnswer(session.id, nextData.question.id, answer);
      setResult(res);
      setQuestionCount((n) => n + 1);
      setPhase('evaluated'); // Seamless workflow: instantly display evaluation score with integrated AI misconception notes!
    } catch (e) {
      alert(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleNext() {
    loadNextQuestion(session.id);
  }

  const question = nextData?.question;
  const evaluation = result?.evaluation;
  const mastery = result?.mastery;
  const masteryPct = Math.round((mastery?.mastery_score || 0) * 100);
  const elapsed = Math.round((Date.now() - startTime) / 60000);
  const misconception = result?.misconceptions?.[0]?.description;

  // ── Phase badge ───────────────────────────────────────────────
  const phaseBadge = {
    loading:   null,
    reading:   <span className="phase-badge recall" style={{ background: 'rgba(92, 225, 230, 0.15)', color: 'var(--c-secondary)', borderColor: 'rgba(92, 225, 230, 0.3)' }}>{t('phaseReading')}</span>,
    recall:    <span className="phase-badge recall">{t('phaseRecall')}</span>,
    evaluated: <span className="phase-badge evaluated">{t('phaseEvaluated')}</span>,
    tutor:     <span className="phase-badge tutor">{t('phaseTutor')}</span>,
    done:      null,
  }[phase];

  // ── DONE screen ───────────────────────────────────────────────
  if (phase === 'done') {
    return (
      <div className="page-wrapper" style={{ textAlign: 'center', maxWidth: 560 }}>
        <div className="completion-emoji">🎉</div>
        <h1 style={{ marginTop: 24, marginBottom: 8 }}>{t('completionTitle')}</h1>
        <p style={{ color: 'var(--c-text-muted)', marginBottom: 8 }}>{unit.title}</p>
        <p style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--c-success)', marginBottom: 32 }}>
          {t('completionSub')} — {masteryPct}% Mastery
        </p>
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 40 }}>
          <div className="glass-card" style={{ textAlign: 'center', padding: '20px 32px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--c-primary)' }}>{questionCount}</div>
            <div style={{ color: 'var(--c-text-muted)', fontSize: '0.85rem' }}>{t('completionAnswered')}</div>
          </div>
          <div className="glass-card" style={{ textAlign: 'center', padding: '20px 32px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--c-secondary)' }}>{elapsed}m</div>
            <div style={{ color: 'var(--c-text-muted)', fontSize: '0.85rem' }}>{t('completionTime')}</div>
          </div>
        </div>
        <button className="btn btn-primary" onClick={onBack} style={{ justifyContent: 'center' }}>
          {t('completionNext')}
        </button>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button className="btn btn-ghost" onClick={onBack} style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
            ← {t('completionNext').replace('←', '').trim()}
          </button>
          {phaseBadge}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {phase !== 'reading' && phase !== 'done' && phase !== 'loading' && (
            <button
              className="btn btn-ghost"
              onClick={() => setPhase('reading')}
              style={{ padding: '6px 12px', fontSize: '0.82rem', borderColor: 'rgba(255,255,255,0.15)' }}
            >
              {t('btnPeekSlide')}
            </button>
          )}
          <div style={{ fontSize: '0.82rem', color: 'var(--c-text-muted)', fontWeight: 600 }}>
            {unit.title}
          </div>
        </div>
      </div>

      {/* ── LOADING ───────────────────────────────────────────── */}
      {phase === 'loading' && (
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, padding: 48 }}>
          <div className="spinner" />
          <span style={{ color: 'var(--c-text-muted)' }}>Loading question...</span>
        </div>
      )}

      {/* ── READING PHASE (SLIDE LEARNING + AI SYNTHESIS) ─────── */}
      {phase === 'reading' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          
          {/* 1. ORIGINAL SLIDES VIEWER CARD */}
          {docId && (
            <div className="glass-card" style={{ borderTop: '4px solid var(--c-secondary)', padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
                <div style={{ fontWeight: 800, fontSize: '1.15rem', color: 'var(--c-text)' }}>
                  <span className="gradient-text">{t('slideOrigTitle')}</span>
                  <span style={{ fontSize: '0.88rem', color: 'var(--c-text-muted)', fontWeight: 600, marginLeft: 10 }}>
                    {fmt('slideOrigPage', { current: currentSlideIndex + 1, total: pages.length, page: currentPage })}
                  </span>
                </div>
                
                {/* Navigation Buttons */}
                {pages.length > 1 && (
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      className="btn btn-ghost"
                      onClick={() => setCurrentSlideIndex((i) => Math.max(0, i - 1))}
                      disabled={currentSlideIndex === 0}
                      style={{ padding: '6px 14px', fontSize: '0.85rem', opacity: currentSlideIndex === 0 ? 0.4 : 1 }}
                    >
                      {t('slidePrev')}
                    </button>
                    <button
                      className="btn btn-ghost"
                      onClick={() => setCurrentSlideIndex((i) => Math.min(pages.length - 1, i + 1))}
                      disabled={currentSlideIndex === pages.length - 1}
                      style={{ padding: '6px 14px', fontSize: '0.85rem', opacity: currentSlideIndex === pages.length - 1 ? 0.4 : 1 }}
                    >
                      {t('slideNext')}
                    </button>
                  </div>
                )}
              </div>

              {/* Quick page selectors pill bar if > 1 page */}
              {pages.length > 1 && (
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
                  {pages.map((pageNum, idx) => (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentSlideIndex(idx)}
                      style={{
                        background: idx === currentSlideIndex ? 'var(--c-secondary)' : 'rgba(255,255,255,0.05)',
                        color: idx === currentSlideIndex ? '#000' : 'var(--c-text-muted)',
                        border: '1px solid rgba(255,255,255,0.15)',
                        padding: '4px 12px',
                        borderRadius: 20,
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      Trang {pageNum}
                    </button>
                  ))}
                </div>
              )}

              {/* Slide Image Container */}
              <div style={{
                background: 'rgba(0, 0, 0, 0.4)',
                borderRadius: 12,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 16,
                minHeight: 250,
                maxHeight: 650,
                overflow: 'hidden'
              }}>
                <img
                  key={currentPage}
                  src={`/api/documents/${docId}/slide/${currentPage}`}
                  alt={`Slide page ${currentPage}`}
                  style={{ maxWidth: '100%', maxHeight: '600px', objectFit: 'contain', borderRadius: 6, boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}
                />
              </div>
            </div>
          )}

          {/* 2. AI SYNTHESIZED STUDY GUIDE CARD */}
          <div className="glass-card" style={{ borderTop: '4px solid var(--c-primary)', padding: 28 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 16, fontSize: '0.85rem', color: 'var(--c-text-muted)' }}>
              <span style={{ fontWeight: 700, color: 'var(--c-primary)', fontSize: '1rem' }}>
                {t('aiSummarySection')}
              </span>
              {unit.estimated_reading_minutes && (
                <span>{fmt('readingTime', { n: unit.estimated_reading_minutes })}</span>
              )}
            </div>

            <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: 16, color: 'var(--c-text)' }}>
              {unit.title}
            </h3>

            {/* Core slide summary */}
            <div style={{ fontSize: '1.02rem', lineHeight: 1.8, color: 'var(--c-text)', marginBottom: 24, background: 'rgba(255, 255, 255, 0.02)', padding: 18, borderRadius: 10, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              {unit.summary}
            </div>

            {/* Learning Objectives */}
            {unit.learning_objectives && unit.learning_objectives.length > 0 && (
              <div style={{ marginBottom: 22 }}>
                <div style={{ fontWeight: 700, color: 'var(--c-primary)', marginBottom: 10, fontSize: '0.95rem' }}>
                  {t('readingObjectives')}
                </div>
                <ul style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6, color: 'var(--c-text-muted)' }}>
                  {unit.learning_objectives.map((item, idx) => (
                    <li key={idx} style={{ lineHeight: 1.5 }}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Key Concepts */}
            {unit.key_concepts && unit.key_concepts.length > 0 && (
              <div style={{ marginBottom: 22 }}>
                <div style={{ fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 10, fontSize: '0.95rem' }}>
                  {t('readingKeyPoints')}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {unit.key_concepts.map((item, idx) => (
                    <span key={idx} style={{ background: 'rgba(92, 225, 230, 0.1)', color: 'var(--c-secondary)', border: '1px solid rgba(92, 225, 230, 0.25)', padding: '6px 12px', borderRadius: 20, fontSize: '0.85rem', fontWeight: 600 }}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Common Misconceptions */}
            {unit.common_misconceptions && unit.common_misconceptions.length > 0 && (
              <div>
                <div style={{ fontWeight: 700, color: 'var(--c-warning)', marginBottom: 10, fontSize: '0.95rem' }}>
                  {t('readingMisconceptions')}
                </div>
                <ul style={{ paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6, color: 'var(--c-text-muted)' }}>
                  {unit.common_misconceptions.map((item, idx) => (
                    <li key={idx} style={{ lineHeight: 1.5 }}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action CTA Button */}
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={handleStartTesting}
              style={{ width: '100%', justifyContent: 'center', padding: '15px 28px', fontSize: '1.05rem', fontWeight: 700, borderRadius: 12 }}
            >
              {result ? t('btnBackToTest') : t('readingReady')}
            </button>
          </div>
        </div>
      )}

      {/* ── RECALL PHASE ─────────────────────────────────────── */}
      {phase === 'recall' && question && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Question card */}
          <div className="glass-card" style={{ borderLeft: '3px solid var(--c-primary)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--c-text-dim)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {fmt('recallSource', { pages: (question.source_pages || []).join(', ') })}
            </div>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, lineHeight: 1.6 }}>{question.question_text}</p>
          </div>

          {/* Answer area */}
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 10, fontSize: '0.9rem' }}>
              {t('recallTitle')}
            </label>
            <textarea
              className="textarea"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={t('recallPlaceholder')}
              style={{ minHeight: 160 }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={!answer.trim() || submitting}
              style={{ minWidth: 180, justifyContent: 'center' }}
            >
              {submitting ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Evaluating...</>
                : t('recallSubmit')}
            </button>
          </div>
        </div>
      )}

      {/* ── EVALUATED PHASE ──────────────────────────────────── */}
      {phase === 'evaluated' && evaluation && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Inline AI Misconception Warning & Future 1:1 Coaching Notice */}
          {(misconception || (evaluation.detected_misconceptions && evaluation.detected_misconceptions.length > 0)) && (
            <div className="glass-card" style={{ borderLeft: '4px solid var(--c-warning)', background: 'rgba(234, 179, 8, 0.08)', padding: '18px 22px' }}>
              <div style={{ fontWeight: 700, color: '#facc15', fontSize: '0.95rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>⚠️ {t('aiMisconceptionNotice') || t('tutorDetectedNotice')}</span>
              </div>
              <div style={{ color: 'var(--c-text)', fontStyle: 'italic', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: 12, background: 'rgba(0,0,0,0.25)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                {misconception || evaluation.detected_misconceptions.join('; ')}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--c-text-muted)', borderTop: '1px dashed rgba(234,179,8,0.3)', paddingTop: 10 }}>
                {t('aiTutorInlineNotice')}
              </div>
            </div>
          )}

          {/* Score summary */}
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--c-text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {t('evalScore')}
                </div>
                <div style={{ fontSize: '3rem', fontWeight: 800, lineHeight: 1 }}>
                  <span className="gradient-text">{Math.round((evaluation.overall_score || 0) * 100)}%</span>
                </div>
              </div>
              {/* Mastery change */}
              {mastery && (
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-text-muted)', marginBottom: 4 }}>Mastery</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: masteryPct >= 80 ? 'var(--c-success)' : 'var(--c-primary)' }}>
                    {masteryPct}%
                  </div>
                </div>
              )}
            </div>
            {/* Score pills */}
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 16 }}>
              {[
                [t('evalCorrectness'), evaluation.dimension_scores?.correctness],
                [t('evalCoverage'), evaluation.dimension_scores?.coverage],
                [t('evalReasoning'), evaluation.dimension_scores?.reasoning],
                [t('evalApplication'), evaluation.dimension_scores?.application],
              ].map(([label, score]) => score !== undefined && (
                <ScorePill key={label} label={label} score={score} />
              ))}
            </div>
          </div>

          {/* Feedback cards */}
          <div>
            <FeedbackCard type="correct" label={t('evalCorrectPoints')} items={evaluation.correct_points} />
            <FeedbackCard type="missing" label={t('evalMissingPoints')} items={evaluation.missing_points} />
            <FeedbackCard type="missing" label={t('evalIncorrectPoints')} items={evaluation.incorrect_points} />
            <FeedbackCard type="misconception" label={t('evalMisconceptions')} items={evaluation.detected_misconceptions} />
          </div>

          {/* AI feedback text */}
          {evaluation.feedback && (
            <div className="glass-card" style={{ borderLeft: '3px solid var(--c-secondary)' }}>
              <div style={{ fontWeight: 700, marginBottom: 8, fontSize: '0.85rem' }}>{t('evalAIComment')}</div>
              <p style={{ color: 'var(--c-text)', lineHeight: 1.7, fontSize: '0.92rem' }}>{evaluation.feedback}</p>
            </div>
          )}

          {/* Reference answer (accordion) */}
          {result.reference_answer && (
            <div>
              <button className="btn btn-ghost" onClick={() => setRefExpanded(!refExpanded)} style={{ fontSize: '0.85rem' }}>
                {refExpanded ? '▼' : '▶'} {t('evalReferenceAnswer')}
              </button>
              {refExpanded && (
                <div className="glass-card" style={{ marginTop: 10, background: 'rgba(92,225,230,0.05)', borderColor: 'rgba(92,225,230,0.2)' }}>
                  <p style={{ fontSize: '0.9rem', lineHeight: 1.7 }}>{result.reference_answer}</p>
                </div>
              )}
            </div>
          )}

          {/* Mastery progress bar */}
          {mastery && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--c-text-muted)', marginBottom: 6 }}>
                <span>Mastery Progress</span>
                <span style={{ color: masteryPct >= 80 ? 'var(--c-success)' : 'var(--c-primary)', fontWeight: 700 }}>{masteryPct}%</span>
              </div>
              <div className="progress-bar-wrap">
                <div className="progress-bar-fill" style={{ width: `${masteryPct}%` }} />
              </div>
              {masteryPct >= 80 && (
                <p style={{ marginTop: 8, color: 'var(--c-success)', fontWeight: 600, fontSize: '0.88rem' }}>
                  ✅ You have mastered this topic!
                </p>
              )}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={handleNext} style={{ minWidth: 180, justifyContent: 'center' }}>
              {t('evalNext')}
            </button>
          </div>
        </div>
      )}

      {/* ── TUTOR PHASE (COMING SOON NOTICE & WORKFLOW BRIDGE) ─ */}
      {phase === 'tutor' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="glass-card" style={{ borderLeft: '4px solid var(--c-warning)', padding: 28 }}>
            <div style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: 12 }}>
              <span className="gradient-text">{t('tutorComingSoonTitle')}</span>
            </div>
            <p style={{ fontSize: '1rem', color: 'var(--c-text)', lineHeight: 1.6, marginBottom: 18 }}>
              {t('tutorComingSoonDesc')}
            </p>
            {misconception && (
              <div style={{ background: 'rgba(234, 179, 8, 0.1)', border: '1px solid rgba(234, 179, 8, 0.3)', padding: '14px 18px', borderRadius: 10, marginTop: 12 }}>
                <div style={{ fontWeight: 700, color: 'var(--c-warning)', fontSize: '0.88rem', marginBottom: 6 }}>
                  {t('tutorDetectedNotice')}
                </div>
                <div style={{ color: 'var(--c-text)', fontStyle: 'italic', fontSize: '0.95rem', lineHeight: 1.5 }}>
                  {misconception}
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={() => setPhase('evaluated')}
              style={{ width: '100%', justifyContent: 'center', padding: '15px 28px', fontSize: '1.05rem', fontWeight: 700, borderRadius: 12 }}
            >
              {t('tutorContinueToEval')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
