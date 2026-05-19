import React, {useEffect, useState, useRef} from 'react';
import Chart from 'chart.js/auto';
import './WorkspaceDashboard.css';

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL?.trim() ||
  (['localhost', '127.0.0.1'].includes(window.location.hostname)
    ? 'http://localhost:8000/api'
    : 'https://api.uprlabs.com/api')
).replace(/\/$/, '');

const parseJsonSafe = async (response) => {
  try {
    return await response.json();
  } catch {
    return null;
  }
};

const WorkspaceDashboard = () => {
  const [activeEntry, setActiveEntry] = useState(null);
  const [history, setHistory] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);

  const[title, setTitle]= useState('');
  const[targetWords, setTargetWords]= useState('');
  const[authorTag, setAuthorTag]= useState('');
  const[bodyText, setBodyText] = useState('');

  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/essays/`);
      if (!response.ok) {
        console.error(`Failed to fetch history: ${response.status} ${response.statusText}`);
        setHistory([]);
        return;
      }
      const data = await parseJsonSafe(response);
      setHistory(Array.isArray(data) ? data : []);
    } catch(error){
      console.error('Failed to fetch history:', error);
      setHistory([]);
    }
  };

  const fetchTrends= async ()=> {
    try {
      const response= await fetch(`${API_BASE_URL}/essays/historical_trends/`);
      if (!response.ok){
        console.error(`Failed to fetch trends: ${response.status} ${response.statusText}`);
        setTrends([]);
        return;
      }
      const data= await parseJsonSafe(response);
      setTrends(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch trends:', error);
      setTrends([]);
    }
  };

  useEffect(()=>{
    fetchHistory();
    fetchTrends();
  }, []);

  useEffect(()=>{
    //Render chart only when no active entry is selected
    if(!activeEntry && trends.length > 0 && chartRef.current){
      if(chartInstance.current){
        chartInstance.current.destroy();
      }

      const labels= trends.map(t => new Date(t.created_at).toLocaleDateString());
      const vocabData = trends.map(t => t.vocab_complexity);
      const gradeData = trends.map(t => t.grade_level);

      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label:'Vocab Complexity (%)',
              data: vocabData,
              borderColor: '#818cf8',
              backgroundColor: 'rgba(129, 140, 248, 0.1)',
              tension: 0.4,
              fill:true
            },
            {
              label: 'Grade Level',
              data: gradeData,
              borderColor: '#22c55e',
              backgroundColor: 'rgba(34, 197, 94, 0.1)',
              tension: 0.4,
              fill:true
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {color: '#cbd5e1'}
            }
          },
          scales: {
            x: {
              ticks: {color: '#94a3b8'},
              grid: {color: '#1e293b'}
            },
            y: {
              ticks: {color: '#94a3b8'},
              grid: {color: '#1e293b'}
            }
          }
        }
      });
    }

    return () => {
      if (chartInstance.current){
        chartInstance.current.destroy();
        chartInstance.current= null;
      }
    };
  }, [trends, activeEntry]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try{
      const response = await fetch (`${API_BASE_URL}/essays/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          target_words: parseInt(targetWords, 10) || 0,
          author_tag: authorTag,
          body_text: bodyText
        })
      });

      if (!response.ok) {
        const errorData = await parseJsonSafe(response);
        console.error('Failed to submit essay:', response.status, errorData || response.statusText);
        return;
      }

      const data = await parseJsonSafe(response);
      if (!data || typeof data !== 'object') {
        console.error('Failed to submit essay: invalid response payload');
        return;
      }
      setActiveEntry(data);

      setTitle('');
      setTargetWords('');
      setAuthorTag('');
      setBodyText('');

      fetchHistory();
      fetchTrends();
    } catch (error) {
      console.error('Failed To Submit Essay', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStateA = () => (
    <>
    <div className="left-column">
      <form className="editor-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="input-group">
            <label>Title</label>
            <input
            type='text'
            className='input-field'
            value={title}
            onChange={(e)=>setTitle(e.target.value)}
            required
            />
          </div>
          <div className='input-group'>
            <label>Target Words</label>
            <input
            type='number'
            className='input-field'
            value={targetWords}
            onChange={(e)=>setTargetWords(e.target.value)}
            required
            />
          </div>
          <div className='input-group'>
            <label>Author Tag</label>
            <input
            type='text'
            className='input-field'
            value={authorTag}
            onChange={(e)=>setAuthorTag(e.target.value)}
            required
            />
          </div>
        </div>
        <div className='input-group' style={{flex:1, marginTop: '1rem'}}>
          <label>Essay Text</label>
          <textarea
          className='input-field textarea-field'
          value={bodyText}
          onChange={(e)=>setBodyText(e.target.value)}
          required
          />
        </div>
        <button type='submit' className='submit-btn' disabled={loading}>
          {loading ? 'Processing...' : 'Analyze Essay'}
        </button>
      </form>
    </div>

    <div className='middle-column'>
      <div className='chart-container'>
        <canvas ref={chartRef}></canvas>
      </div>
    </div>

    <div className='right-column'>
      <h3 style={{marginTop: 0, marginBottom: '1rem', color: 'var(--slate-100)'}}>History Log</h3>
      <table className='ledger-table'>
        <thead>
          <tr>
            <th>Title</th>
            <th>Date</th>
            <th>Grade Level</th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry)=> (
            <tr key={entry.id} className='ledger-row' onClick={()=> setActiveEntry(entry)}>
              <td>{entry.title}</td>
              <td>{new Date(entry.created_at).toLocaleDateString()}</td>
              <td>{entry.metrics?.grade_level || '-'} </td>
            </tr>
          ))}
          {history.length === 0 && (
            <tr>
              <td colSpan="3" style={{textAlign: 'center', paddingTop: '2rem'}}>No submissions yet.</td>
        
            </tr>
          )}
        </tbody>
      </table>
    </div>
    </>

  );
  const renderStateB = () => {
    const metrics = activeEntry?.metrics || {};
    const structuralFixes = Array.isArray(metrics.structural_fixes)
      ? metrics.structural_fixes
      : Array.isArray(metrics.structural_feedback)
        ? metrics.structural_feedback.map((item) => (
            typeof item === 'string' ? { type: 'Feedback', message: item } : item
          ))
        : [];
    const targetWordCount = activeEntry?.target_words ?? activeEntry?.targetWords ?? '-';
    const bodyTextValue = typeof activeEntry?.body_text === 'string' ? activeEntry.body_text : '';

    return (
      <>
    <div className='left-column' style={{flex:1}}>
      <button className='back-btn' onClick={()=> setActiveEntry(null)}>
        &larr; Back to Dashboard
      </button>
      <h2 style={{marginTop: 0, marginBottom: '2rem'}}>{activeEntry.title}</h2>
      <div className='bento-grid'>
        <div className='bento-tile'>
          <span className='bento-label'>Grade Level</span>
          <span className='bento-value'>{metrics.grade_level ?? '-'}</span>

        </div>
        <div className='bento-tile'>
          <span className='bento-label'>Reading Ease</span>
          <span className='bento-value'>{metrics.reading_ease ?? '-'}</span>

        </div>
        <div className='bento-tile'>
          <span className='bento-label'>Vocab Footprint</span>
          <span className='bento-value'>{metrics.vocab_complexity ?? '-'}%</span>

        </div>
        <div className='bento-tile'>
          <span className='bento-label'>Word Count / Target</span>
          <span className='bento-value'>
            {metrics.word_count ?? '-'} <span style={{fontSize:'1rem', color:'var(--slate-400)'}}>/ {targetWordCount}</span>

          </span>
        </div>
      </div>

      <div className='warnings-panel' style={{marginTop: '2rem'}}>
        <h3 style={{margin: 0, color: 'var(--slate-100)'}}>Structural Review</h3>
        {structuralFixes.length > 0 ? (
          structuralFixes.map((fix,idx)=>(
            <div key={idx} className='warning-alert'>
              <span className='warning-type'>{fix.type || 'Feedback'}</span>
              <span className='warning-message'>{fix.message || String(fix)}</span>
              </div>
          ))
        ) : (
          <div style={{color: 'var(--green-500)', padding: '1rem', backgroundColor: 'rgba(34,197,94,0.1)', borderRadius:'8px'}}>
            No structural vulnerabilities found!
            </div>
        
        )}
      </div>
    </div>

    <div className='middle-column' style={{flex:2}}>
      <div className='essay-canvas'>
        {bodyTextValue.split('\n').map((paragraph, idx) => (
          <p key={idx}>{paragraph}</p>
        ))}
      </div>
    </div>
      </>
    );
  };

  return (
    <div className='workspace-container'>
      <div className='workspace-header'>
        <h1 className='workspace-title'>Critique Counter</h1>
      </div>
      <div className='workspace-content'>
        {!activeEntry? renderStateA(): renderStateB()}
      </div>
    </div>
  );
};

export default WorkspaceDashboard
