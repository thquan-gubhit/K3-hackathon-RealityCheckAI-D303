import { useState, useEffect } from 'react';
import './index.css';
import { LangProvider } from './context/LangContext';
import { getKnowledgeMap, getUserProgress, createLearningSession, listDocuments } from './api/client';
import LandingPage from './pages/LandingPage';
import LearningPath from './pages/LearningPath';
import StudyRoom from './pages/StudyRoom';
import Sidebar from './components/layout/Sidebar';

// App state machine: landing | path | study
export default function App() {
  const [screen, setScreen] = useState('landing');
  const [document, setDocument] = useState(null);
  const [units, setUnits] = useState([]);
  const [progress, setProgress] = useState({});
  const [activeUnit, setActiveUnit] = useState(null);
  const [activeSession, setActiveSession] = useState(null);

  // Auto-restore previous document session from localStorage so users don't waste AI tokens re-uploading on reload!
  useEffect(() => {
    const savedDocId = localStorage.getItem('reality_check_active_doc');
    if (savedDocId) {
      listDocuments()
        .then((data) => {
          if (Array.isArray(data)) {
            const found = data.find((d) => d.id === savedDocId && d.status === 'ready');
            if (found) {
              setDocument(found);
              setScreen('path');
            }
          }
        })
        .catch(() => {});
    }
  }, []);

  // Load knowledge map after document ready
  useEffect(() => {
    if (!document) return;
    getKnowledgeMap(document.id)
      .then((data) => setUnits(data.units || data.knowledge_units || []))
      .catch(() => {});
  }, [document]);

  // Refresh progress periodically
  useEffect(() => {
    if (screen === 'landing') return;
    function load() {
      getUserProgress()
        .then((data) => {
          const map = {};
          for (const ku of data.knowledge_units || []) map[ku.knowledge_unit_id] = ku;
          setProgress(map);
        })
        .catch(() => {});
    }
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [screen]);

  function handleDocumentReady(doc) {
    localStorage.setItem('reality_check_active_doc', doc.id);
    setDocument(doc);
    setScreen('path');
  }

  function handleStartUnit(unit, session) {
    setActiveUnit(unit);
    setActiveSession(session);
    setScreen('study');
  }

  function handleBackToPath() {
    setScreen('path');
    setActiveUnit(null);
    setActiveSession(null);
    // Refresh progress
    getUserProgress()
      .then((data) => {
        const map = {};
        for (const ku of data.knowledge_units || []) map[ku.knowledge_unit_id] = ku;
        setProgress(map);
      })
      .catch(() => {});
  }

  function handleSelectDocument(doc) {
    if (doc.id === document?.id && screen === 'path') return;
    localStorage.setItem('reality_check_active_doc', doc.id);
    setDocument(doc);
    setActiveUnit(null);
    setActiveSession(null);
    setScreen('path');
  }

  function handleNewUpload() {
    localStorage.removeItem('reality_check_active_doc');
    setActiveUnit(null);
    setActiveSession(null);
    setScreen('landing');
  }

  async function handleSelectSidebarUnit(unitId) {
    const target = units.find((u) => u.id === unitId);
    if (!target || !document) return;
    try {
      const session = await createLearningSession(document.id, target.id);
      setActiveUnit(target);
      setActiveSession(session);
      setScreen('study');
    } catch (e) {
      alert(e.message || 'Failed to start topic');
    }
  }

  const showSidebar = screen !== 'landing';

  return (
    <LangProvider>
      <div className="app-layout">
        {/* Sidebar — visible after upload or when browsing courses */}
        {showSidebar && (
          <Sidebar
            screen={screen}
            units={units}
            activeUnitId={activeUnit?.id}
            progress={progress}
            document={document}
            onSelectDocument={handleSelectDocument}
            onNewUpload={handleNewUpload}
            onSelectUnit={handleSelectSidebarUnit}
          />
        )}

        <div className={`main-content${showSidebar ? '' : ' no-sidebar'}`}>
          {screen === 'landing' && (
            <LandingPage onDocumentReady={handleDocumentReady} />
          )}

          {screen === 'path' && document && (
            <LearningPath
              document={document}
              units={units}
              onStartUnit={handleStartUnit}
            />
          )}

          {screen === 'study' && activeUnit && activeSession && (
            <StudyRoom
              document={document}
              unit={activeUnit}
              session={activeSession}
              onBack={handleBackToPath}
            />
          )}
        </div>
      </div>
    </LangProvider>
  );
}
