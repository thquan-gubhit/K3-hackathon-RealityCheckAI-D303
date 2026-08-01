import { useState, useCallback } from 'react';
import { useLang } from '../context/LangContext';
import { uploadDocument, processDocument, checkHealth } from '../api/client';
import { useEffect } from 'react';

const STEPS = ['uploadStep1', 'uploadStep2', 'uploadStep3'];

export default function LandingPage({ onDocumentReady }) {
  const { t, lang } = useLang();
  const [dragOver, setDragOver] = useState(false);
  const [step, setStep] = useState(-1); // -1 = idle, 0/1/2 = processing steps
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => setIsOnline(true))
      .catch(() => setIsOnline(false));
  }, []);

  async function handleFile(file) {
    if (!file || !file.name.endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    setError(null);
    try {
      // Step 0: upload
      setStep(0);
      const doc = await uploadDocument(file);
      // Step 1: process
      setStep(1);
      await processDocument(doc.id);
      // Step 2: done
      setStep(2);
      setTimeout(() => onDocumentReady(doc), 800);
    } catch (e) {
      setError(e.message);
      setStep(-1);
    }
  }

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, []);

  const onInputChange = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  };

  const isProcessing = step >= 0 && step < 2;

  return (
    <div className="page-wrapper" style={{ maxWidth: 680, marginTop: 80, width: '100%' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <h1 style={{ fontSize: '2.8rem', fontWeight: 800, marginBottom: 12 }}>
          <span className="gradient-text">Reality Check AI</span>
        </h1>
        <p style={{ fontSize: '1.15rem', color: 'var(--c-text-muted)', marginBottom: 6 }}>
          {t('tagline')}
        </p>
        <p style={{ fontSize: '0.9rem', color: 'var(--c-text-dim)' }}>{t('taglineSub')}</p>

        {/* Status dot */}
        {isOnline !== null && (
          <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, fontSize: '0.8rem', color: isOnline ? 'var(--c-success)' : 'var(--c-danger)' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: isOnline ? 'var(--c-success)' : 'var(--c-danger)', display: 'inline-block' }} />
            {isOnline ? t('online') : t('offline')}
          </div>
        )}
      </div>

      {/* Upload area */}
      {step < 0 ? (
        <label
          htmlFor="pdf-input"
          className={`drop-zone${dragOver ? ' drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          style={{ display: 'block', outline: 'none', cursor: 'pointer' }}
        >
          <div className="upload-icon">📄</div>
          <h3 style={{ marginBottom: 8, fontSize: '1.1rem' }}>{t('uploadTitle')}</h3>
          <p style={{ color: 'var(--c-text-muted)', fontSize: '0.9rem' }}>{t('uploadHint')}</p>
          <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }} onChange={onInputChange} />
        </label>
      ) : (
        /* Processing steps */
        <div className="glass-card" style={{ padding: 40 }}>
          <div className="step-indicator" style={{ marginBottom: 32 }}>
            {STEPS.map((stepKey, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                  <div className={`step-dot${step > i ? ' done' : step === i ? ' active' : ''}`}>
                    {step > i ? '✓' : i + 1}
                  </div>
                  <span className="step-label">{t(stepKey)}</span>
                </div>
                {i < STEPS.length - 1 && <div className="step-line" />}
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center' }}>
            {step < 2 && <div className="spinner" />}
            <span style={{ color: 'var(--c-text-muted)', fontSize: '0.9rem' }}>
              {step < 2 ? t('uploadProcessing') : t('uploadDone')}
            </span>
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, color: 'var(--c-danger)', fontSize: '0.9rem' }}>
          ⚠️ {error}
        </div>
      )}

      {/* How it works */}
      {step < 0 && (
        <div style={{ marginTop: 48, display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
          {[
            { icon: '📤', label: lang === 'vi' ? 'Upload PDF' : 'Upload PDF', desc: lang === 'vi' ? 'Tải lên tài liệu học của bạn' : 'Upload your learning material' },
            { icon: '🤖', label: lang === 'vi' ? 'AI phân tích' : 'AI Analysis', desc: lang === 'vi' ? 'AI đọc & tạo bộ câu hỏi' : 'AI reads & generates questions' },
            { icon: '🧠', label: lang === 'vi' ? 'Kiểm tra & Học' : 'Test & Learn', desc: lang === 'vi' ? 'Active recall + Đánh giá đa chiều' : 'Active recall + Multi-dim scoring' },
          ].map((step, i) => (
            <div key={i} className="glass-card" style={{ textAlign: 'center', padding: '24px 16px' }}>
              <div style={{ fontSize: '2rem', marginBottom: 10 }}>{step.icon}</div>
              <div style={{ fontWeight: 700, marginBottom: 6, fontSize: '0.9rem' }}>{step.label}</div>
              <div style={{ color: 'var(--c-text-muted)', fontSize: '0.8rem' }}>{step.desc}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
