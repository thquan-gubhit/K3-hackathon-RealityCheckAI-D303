import { useState, useEffect } from 'react';
import './index.css';
import { LangProvider } from './context/LangContext';
import { getKnowledgeMap, getUserProgress } from './api/client';
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

  const showSidebar = screen !== 'landing' && units.length > 0;

  return (
    <LangProvider>
      <div className="app-layout">
        {/* Sidebar — only visible after upload */}
        {showSidebar && (
          <Sidebar
            units={units}
            activeUnitId={activeUnit?.id}
            progress={progress}
            documentName={document?.filename}
            onSelectUnit={(unitId) => {
              // Switch to path screen for unit selection
              setScreen('path');
            }}
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
