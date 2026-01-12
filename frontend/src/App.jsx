import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';

// SearchPage removed
import ChatPage from './pages/ChatPage';
import HistoryPage from './pages/HistoryPage';

// useNotifications removed
import { useLeads } from './hooks/useLeads';
import client from './api/client';

function App() {
  const [view, setView] = useState('home');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  // searchQuery removed

  // Custom Hooks
  // notifications hook removed

  // Chat State (Lifted Up)
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Hello! I can help you analyze your leads. Ask me anything about your data' }
  ]);

  const {
    file,
    handleFileUpload,
    analyzeLeads,
    cancelAnalysis,
    loading,
    progressMessage,
    error,
    metrics,
    allLeads,
    highPriorityLeads,
    currentFilename,
    setMetrics,
    setAllLeads,
    setHighPriorityLeads,
    setCurrentFilename
  } = useLeads();

  // History Detail Logic (kept here to coordinate view switch)
  // Can be moved to a hook if it gets complex
  const [predictionHistory, setPredictionHistory] = useState([]); // Needed for dashboard chart

  // Cache for history details to avoid re-fetching
  const historyCache = useRef({});
  const [loadingHistoryId, setLoadingHistoryId] = useState(null);

  // Load history for charts on mount
  useEffect(() => {
    const loadHistorySummary = async () => {
      try {
        const res = await client.get('/prediction-history');
        setPredictionHistory(res.data.history);
      } catch (e) { console.error(e); }
    };
    loadHistorySummary();
  }, [loading]); // Reload history after analysis finishes

  // handleSearch removed

  const handleHistoryClick = async (runId) => {
    if (historyCache.current[runId]) {
      const data = historyCache.current[runId];
      updateStateFromHistory(data);
      return;
    }

    setLoadingHistoryId(runId);
    try {
      const res = await client.get(`/prediction-history/${runId}`);
      const data = res.data;

      // Cache it
      historyCache.current[runId] = data;

      updateStateFromHistory(data);
    } catch (err) {
      console.error(err);
      // Could show a toast here
    } finally {
      setLoadingHistoryId(null);
    }
  };

  const updateStateFromHistory = (data) => {
    const leads = data.results;
    const high = leads.filter(l => l.priority === 'High');

    setAllLeads(leads);
    setHighPriorityLeads(high);
    setCurrentFilename(data.filename);
    setMetrics({
      total: leads.length,
      high: high.length,
      medium: leads.filter(l => l.priority === 'Medium').length,
      low: leads.filter(l => l.priority === 'Low').length,
      accuracy: data.accuracy_metrics
    });

    setView('dashboard');
  };

  const onAnalyzeWrapper = async () => {
    const success = await analyzeLeads();
    if (success) {
      // refreshNotifications removed
      setView('dashboard');
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      <Sidebar
        currentView={view}
        setView={setView}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={
            view === 'home' ? 'Home' :
              view === 'dashboard' ? 'Dashboard' :
                view === 'search' ? 'Search Results' :
                  view === 'chat' ? 'AI Assistant' : 'History'
          }
          setIsMobileOpen={setIsMobileOpen}
        // Props removed
        />

        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          {view === 'home' && (
            <HomePage
              file={file}
              handleFileUpload={handleFileUpload}
              handleAnalyze={onAnalyzeWrapper}
              cancelAnalysis={cancelAnalysis}
              loading={loading}
              progressMessage={progressMessage}
              error={error}
            />
          )}
          {view === 'dashboard' && (
            <DashboardPage
              metrics={metrics}
              predictionHistory={predictionHistory}
              allLeads={allLeads}
              highPriorityLeads={highPriorityLeads}
            />
          )}
          {/* SearchPage removed */}
          {view === 'chat' && (
            <ChatPage
              metrics={metrics}
              filename={currentFilename}
              chatMessages={chatMessages}
              setChatMessages={setChatMessages}
            />
          )}
          {view === 'history' && (
            <HistoryPage
              setView={setView}
              handleHistoryClick={handleHistoryClick}
              loadingHistoryId={loadingHistoryId}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
