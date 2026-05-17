import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './WorkspaceDashboard.css';

const API_BASE_URL = 'http://localhost:8000/api';

const WorkspaceDashboard = () => {
  const [activeEntry, setActiveEntry] = useState(null);
  const [history, setHistory] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Form State
  const [title, setTitle] = useState('');
  const [targetWords, setTargetWords] = useState('');
  const [authorTag, setAuthorTag] = useState('');
  const [bodyText, setBodyText] = useState('');

  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/essays/`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/essays/historical_trends/`);
      if (response.ok) {
        const data = await response.json();
        setTrends(data);
      }
    } catch (error) {
      console.error('Failed to fetch trends:', error);
    }
  };

  useEffect(() => {
    fetchHistory();
    fetchTrends();
  }, []);

  useEffect(() => {
    // Render chart only when no active entry is selected and we have trends
    if (!activeEntry && trends.length > 0 && chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      const labels = trends.map(t => new Date(t.created_at).toLocaleDateString());
      const vocabData = trends.map(t => t.vocab_complexity);
      const gradeData = trends.map(t => t.grade_level);

      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Vocab Complexity (%)',
              data: vocabData,
              borderColor: '#818cf8', // indigo-400
              backgroundColor: 'rgba(129, 140, 248, 0.1)',
              tension: 0.4,
              fill: true
            },
            {
              label: 'Grade Level',
              data: gradeData,
              borderColor: '#22c55e', // green-500
              backgroundColor: 'rgba(34, 197, 94, 0.1)',
              tension: 0.4,
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#cbd5e1' }
            }
          },
          scales: {
            x: {
              ticks: { color: '#94a3b8' },
              grid: { color: '#1e293b' }
            },
            y: {
              ticks: { color: '#94a3b8' },
              grid: { color: '#1e293b' }
            }
          }
        }
      });
    }
    
    // Cleanup on unmount or re-render
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, [trends, activeEntry]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/essays/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          target_words: parseInt(targetWords) || 0,
          author_tag: authorTag,
          body_text: bodyText
        })
      });
      
      const data = await response.json();
      setActiveEntry(data);
      
      // Reset form fields
      setTitle('');
      setTargetWords('');
      setAuthorTag('');
      setBodyText('');
      
      // Refresh side data mapping to capture new inputs
      fetchHistory();
      fetchTrends();
    } catch (error) {
      console.error('Failed to submit essay:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStateA = () => (
    <>
      <div className="left-column">
        <form className="editor-form" onSubmit={handleSubmit}>
          {/* Dual field header form (Title, Target, Tag) */}
          <div className="form-row">
            <div className="input-group">
              <label>Title</label>
              <input 
                type="text" 
                className="input-field" 
                value={title} 
                onChange={(e) => setTitle(e.target.value)} 
                required 
              />
            </div>
            <div className="input-group">
              <label>Target Words</label>
              <input 
                type="number" 
                className="input-field" 
                value={targetWords} 
                onChange={(e) => setTargetWords(e.target.value)} 
                required 
              />
            </div>
            <div className="input-group">
              <label>Author Tag</label>
              <input 
                type="text" 
                className="input-field" 
                value={authorTag} 
                onChange={(e) => setAuthorTag(e.target.value)} 
                required 
              />
            </div>
          </div>
          {/* Text editor area */}
          <div className="input-group" style={{ flex: 1, marginTop: '1rem' }}>
            <label>Essay Text</label>
            <textarea 
              className="input-field textarea-field" 
              value={bodyText} 
              onChange={(e) => setBodyText(e.target.value)} 
              required 
            />
          </div>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Processing...' : 'Analyze Essay'}
          </button>
        </form>
      </div>

      <div className="middle-column">
        {/* Line graph updating time-series indices using Chart.js */}
        <div className="chart-container">
          <canvas ref={chartRef}></canvas>
        </div>
      </div>

      <div className="right-column">
        <h3 style={{ marginTop: 0, marginBottom: '1rem', color: 'var(--slate-100)' }}>History Log</h3>
        {/* Side scrollable ledger table displaying historical submission logs */}
        <table className="ledger-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Date</th>
              <th>Grade Level</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry) => (
              <tr key={entry.id} className="ledger-row" onClick={() => setActiveEntry(entry)}>
                <td>{entry.title}</td>
                <td>{new Date(entry.created_at).toLocaleDateString()}</td>
                <td>{entry.metrics?.grade_level || '-'}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan="3" style={{ textAlign: 'center', paddingTop: '2rem' }}>No submissions yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );

  const renderStateB = () => (
    <>
      <div className="left-column" style={{ flex: 1 }}>
        <button className="back-btn" onClick={() => setActiveEntry(null)}>
          &larr; Back to Dashboard
        </button>
        <h2 style={{ marginTop: 0, marginBottom: '2rem' }}>{activeEntry.title}</h2>
        
        {/* 4-tile Bento block (Grade Level, Ease Index, Vocabulary Footprint, Target tracker) */}
        <div className="bento-grid">
          <div className="bento-tile">
            <span className="bento-label">Grade Level</span>
            <span className="bento-value">{activeEntry.metrics.grade_level}</span>
          </div>
          <div className="bento-tile">
            <span className="bento-label">Reading Ease</span>
            <span className="bento-value">{activeEntry.metrics.reading_ease}</span>
          </div>
          <div className="bento-tile">
            <span className="bento-label">Vocab Footprint</span>
            <span className="bento-value">{activeEntry.metrics.vocab_complexity}%</span>
          </div>
          <div className="bento-tile">
            <span className="bento-label">Word Count / Target</span>
            <span className="bento-value">
              {activeEntry.metrics.word_count} <span style={{fontSize: '1rem', color: 'var(--slate-400)'}}>/ {activeEntry.target_words}</span>
            </span>
          </div>
        </div>

        {/* Dedicated warning panel rendering rule errors parsed from the JSON payload */}
        <div className="warnings-panel" style={{ marginTop: '2rem' }}>
          <h3 style={{ margin: 0, color: 'var(--slate-100)' }}>Structural Review</h3>
          {activeEntry.metrics.structural_fixes && activeEntry.metrics.structural_fixes.length > 0 ? (
            activeEntry.metrics.structural_fixes.map((fix, idx) => (
              <div key={idx} className="warning-alert">
                <span className="warning-type">{fix.type}</span>
                <span className="warning-message">{fix.message}</span>
              </div>
            ))
          ) : (
            <div style={{ color: 'var(--green-500)', padding: '1rem', backgroundColor: 'rgba(34, 197, 94, 0.1)', borderRadius: '8px' }}>
              No structural vulnerabilities found! Excellent writing.
            </div>
          )}
        </div>
      </div>

      <div className="middle-column" style={{ flex: 2 }}>
        {/* High-legibility serif text viewport component */}
        <div className="essay-canvas">
          {activeEntry.body_text.split('\n').map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
      </div>
    </>
  );

  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <h1 className="workspace-title">CritiqueCounter</h1>
      </div>
      <div className="workspace-content">
        {!activeEntry ? renderStateA() : renderStateB()}
      </div>
    </div>
  );
};

export default WorkspaceDashboard;
