import React, { useMemo } from 'react';
import Page from '../components/Page';
import Card from '../components/Card';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import './SmartAnalysis.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend, Title);

export default function SmartAnalysis({ history = [] }) {
  // compute counts from history (Positive, Neutral, Negative)
  const counts = useMemo(() => {
    let pos = 0, neu = 0, neg = 0;
    history.forEach((h) => {
      const s = (h.sentiment || '').toString().toLowerCase();
      if (s.includes('pos')) pos++;
      else if (s.includes('neg')) neg++;
      else neu++;
    });
    return { pos, neu, neg };
  }, [history]);

  const chartData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Sentiment Count',
        data: [counts.pos, counts.neu, counts.neg],
        backgroundColor: ['#22c55e', '#3b82f6', '#ef4444'],
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: false, text: 'Sentiment distribution' },
    },
    scales: {
      x: { title: { display: false } },
      y: { beginAtZero: true, ticks: { precision:0 } },
    },
  };

  // compute peak sentiment safely
  const peakSentiment = useMemo(() => {
    const arr = [['Positive', counts.pos], ['Neutral', counts.neu], ['Negative', counts.neg]];
    const sorted = arr.sort((a,b)=>b[1]-a[1]);
    return sorted[0] ? sorted[0][0] : '—';
  }, [counts]);

  return (
    <Page title="📊 Smart Analysis" subtitle="Search history and view sentiment distribution">
      <div className="grid-analysis">
        {/* full-width history */}
        <div className="history-col">
          <Card title="Conversation History" subtitle="All recorded transcripts">
            <div style={{ maxHeight: 280, overflow: 'auto' }}>
              {history.length === 0 && <p className="muted">No records found.</p>}
              <ul style={{ marginTop: 8 }}>
                {history.map((h, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>
                    <b>{h.date || h.time || '-'}</b>: "{h.transcript || h.text}" → <b>{h.sentiment}</b>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        </div>

        {/* analytics + insights below */}
        <div className="analytics-row">
          <Card title="Analytics" subtitle="Sentiment distribution">
            <div style={{ height: 360 }}>
              <Bar options={options} data={chartData} />
            </div>
          </Card>

          <Card title="Insights & Conclusions" subtitle="Summary">
            <ul>
              <li>Most conversations trend <b>{peakSentiment}</b> (based on current data).</li>
              <li>Total conversations: <b>{history.length}</b></li>
              <li>📌 Customers respond well to empathy and concise answers.</li>
              <li>📌 Negative tones often need follow-up to recover confidence.</li>
            </ul>
          </Card>
        </div>

        {/* stacked conclusions full width */}
        <div className="conclusions-row">
          <Card title="Actionable Takeaways" subtitle="Actionable takeaways">
            <ol>
              <li>Customers respond favorably when reps mirror tone and show empathy.</li>
              <li>Prioritize follow-ups for negative interactions within 24 hours.</li>
              <li>Provide short, solution-focused responses to keep momentum.</li>
            </ol>
          </Card>
        </div>
      </div>
    </Page>
  );
}
