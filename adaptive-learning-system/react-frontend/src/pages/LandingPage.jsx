import { useState, useCallback } from 'react';
import { useLang } from '../context/LangContext';
import { uploadDocument, processDocument, checkHealth, listDocuments } from '../api/client';
import { useEffect } from 'react';

const STEPS = ['uploadStep1', 'uploadStep2', 'uploadStep3'];

export default function LandingPage({ onDocumentReady }) {
  const { t, lang } = useLang();
  const [dragOver, setDragOver] = useState(false);
  const [step, setStep] = useState(-1); // -1 = idle, 0/1/2 = processing steps
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(null);
  const [thinkIdx, setThinkIdx] = useState(0);
  const [savedDocs, setSavedDocs] = useState([]);

  useEffect(() => {
    checkHealth()
      .then(() => setIsOnline(true))
      .catch(() => setIsOnline(false));

    listDocuments()
      .then((data) => {
        if (Array.isArray(data)) {
          const ready = data.filter((d) => d.status === 'ready');
          const uniqueMap = new Map();
          for (const doc of ready) {
            if (!uniqueMap.has(doc.filename) || new Date(doc.created_at) > new Date(uniqueMap.get(doc.filename).created_at)) {
              uniqueMap.set(doc.filename, doc);
            }
          }
          setSavedDocs(Array.from(uniqueMap.values()).slice(0, 6));
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (step === 1) {
      const timer = setInterval(() => {
        setThinkIdx((idx) => (idx + 1) % 4);
      }, 2600);
      return () => clearInterval(timer);
    }
  }, [step]);

  async function handleFile(file) {
    if (!file || !file.name.endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    setError(null);
    setThinkIdx(0);
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

  const thinkingMessagesVi = [
    '📖 Đang bóc tách và phân tích các trang slide PDF...',
    '🧠 Trí tuệ AI đang suy luận các đơn vị kiến thức trọng tâm...',
    '🔗 Đang liên kết các khái niệm và bóc tách điểm ngộ nhận...',
    '⚡ Đang đóng gói Bản đồ lộ trình học cá nhân hóa cho bạn!'
  ];
  const thinkingMessagesEn = [
    '📖 Parsing and inspecting slide document pages...',
    '🧠 AI intelligence identifying core topic units...',
    '🔗 Mapping concept relationships and potential misconceptions...',
    '⚡ Finalizing your personalized adaptive study roadmap!'
  ];

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
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {step < 2 && <div className="spinner" style={{ width: 22, height: 22, borderWidth: 3 }} />}
              <span style={{ color: 'var(--c-text)', fontSize: '0.98rem', fontWeight: 600 }}>
                {step === 0 ? t('uploadProcessing') : step === 1 ? (lang === 'vi' ? thinkingMessagesVi[thinkIdx] : thinkingMessagesEn[thinkIdx]) : t('uploadDone')}
              </span>
            </div>
            {step === 1 && (
              <div className="progress-bar-wrap" style={{ width: '75%', height: '6px' }}>
                <div className="progress-bar-fill" style={{ width: `${(thinkIdx + 1) * 25}%`, background: 'linear-gradient(90deg, var(--c-primary), #5ce1e6)', transition: 'width 0.5s ease' }} />
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 10, color: 'var(--c-danger)', fontSize: '0.9rem' }}>
          ⚠️ {error}
        </div>
      )}

      {/* Existing Library right on Landing Page to save token processing & time */}
      {step < 0 && savedDocs.length > 0 && (
        <div style={{ marginTop: 44 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--c-text)' }}>
              <span>📚 {lang === 'vi' ? 'Slide Đã Tải & Phân Tích Sẵn (0 Tốn Token)' : 'Saved & Analyzed Slides (0 Token Cost)'}</span>
            </h3>
            <span style={{ fontSize: '0.78rem', padding: '3px 10px', background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e', borderRadius: '20px', fontWeight: 700 }}>
              ⚡ {lang === 'vi' ? 'Mở ngay tức thì' : 'Instant Load'}
            </span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: 14 }}>
            {savedDocs.map((docItem) => (
              <div
                key={docItem.id}
                className="glass-card"
                onClick={() => onDocumentReady(docItem)}
                style={{
                  padding: '14px 18px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  border: '1px solid var(--c-border)',
                  transition: 'all 0.2s ease',
                  background: 'rgba(255,255,255,0.02)'
                }}
                onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--c-primary)'; e.currentTarget.style.background = 'rgba(124, 58, 237, 0.08)'; }}
                onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--c-border)'; e.currentTarget.style.background = 'rgba(255,255,255,0.02)'; }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, overflow: 'hidden', flex: 1 }}>
                  <span style={{ fontSize: '1.5rem' }}>📄</span>
                  <div style={{ overflow: 'hidden', flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.92rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--c-text)' }}>
                      {docItem.filename}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--c-text-muted)', marginTop: 3, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span>{docItem.page_count || '?'} {lang === 'vi' ? 'trang' : 'pages'}</span>
                      <span>•</span>
                      <span style={{ color: '#22c55e', fontWeight: 600 }}>Ready 🟢</span>
                    </div>
                  </div>
                </div>
                <button className="btn btn-ghost" style={{ padding: '6px 10px', fontSize: '0.8rem', fontWeight: 700, color: 'var(--c-primary)', marginLeft: 8 }}>
                  {lang === 'vi' ? 'Mở →' : 'Open →'}
                </button>
              </div>
            ))}
          </div>
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
