import React, { useRef, useState, useEffect } from 'react';
import Page from '../components/Page';
import Card from '../components/Card';
import { postForm } from '../api';
import './RealTimeListening.css';

export default function RealTimeListening({ history, setHistory }) {
  const [recording, setRecording] = useState(false);
  const [status, setStatus] = useState('⏹️ Stopped');
  const [result, setResult] = useState({
    transcript: 'Waiting for input...',
    sentiment: 'Neutral',
    tone: 'Detecting...',
    date: '',
    explanation: 'No explanation yet.',
  });

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  // small local sentiment fallback (keeps your original analyzeLocal behavior)
  const isEnglish = (text) => /^[\x00-\x7F]*$/.test(text);

  const analyzeLocal = (text, sentimentFromAPI) => {
    let tone = 'Neutral';
    let explanation = 'No clear sentiment detected.';
    if (!isEnglish(text)) {
      return {
        sentiment: sentimentFromAPI || 'Unknown',
        tone: 'Neutral',
        explanation: '⚠️ Non-English text detected. Enable translation for deeper insights.',
      };
    }
    const lower = text.toLowerCase();
    if (/(good|great|happy|love|awesome|nice)/.test(lower)) {
      tone = 'Friendly';
      explanation = `The customer said: "${text}". Their words suggest satisfaction and positivity.`;
    } else if (/(bad|angry|cancel|refund|terrible|worst)/.test(lower)) {
      tone = 'Upset';
      explanation = `The customer mentioned: "${text}". Words like cancel/refund indicate dissatisfaction.`;
    } else {
      explanation = `The customer said: "${text}". The statement appears neutral without strong emotion.`;
    }
    return { sentiment: sentimentFromAPI || 'Neutral', tone, explanation };
  };

  // Safe start/stop with robust checks
  const toggleRecording = async () => {
    // START recording
    if (!recording) {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setStatus('Microphone not available');
          return;
        }

        // ask for microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;

        // ensure MediaRecorder supported
        if (typeof MediaRecorder === 'undefined') {
          setStatus('MediaRecorder not supported in this browser');
          // stop tracks
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

        // reset chunks
        chunksRef.current = [];

        const mr = new MediaRecorder(stream);
        mediaRecorderRef.current = mr;

        mr.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
        };

        mr.onstop = async () => {
          // if no audio collected
          if (!chunksRef.current.length) {
            const newRecord = {
              transcript: 'No speech detected.',
              sentiment: 'Neutral',
              tone: 'Detecting...',
              date: new Date().toLocaleString(),
              explanation: 'No audio captured.',
            };
            setResult(newRecord);
            if (setHistory) setHistory((h) => [newRecord, ...(h || [])]);
            return;
          }

          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', blob, 'recording.webm');

          try {
            const data = await postForm('/analyze-audio', formData);

            // backend might return { text, sentiment, explanation }
            const local = analyzeLocal(data?.text || '', data?.sentiment);

            const newRecord = {
              transcript: data?.text || 'No speech detected.',
              sentiment: local.sentiment,
              tone: local.tone,
              date: new Date().toLocaleString(),
              explanation: local.explanation,
            };

            setResult(newRecord);
            if (setHistory) setHistory((h) => [newRecord, ...(h || [])]);
          } catch (err) {
            console.error('Error sending audio:', err);
            const errRec = {
              transcript: 'Error transcribing audio',
              sentiment: 'Error',
              tone: 'Error',
              date: new Date().toLocaleString(),
              explanation: String(err.message || err),
            };
            setResult(errRec);
            if (setHistory) setHistory((h) => [errRec, ...(h || [])]);
          } finally {
            // always release media tracks
            if (streamRef.current) {
              streamRef.current.getTracks().forEach((t) => t.stop());
              streamRef.current = null;
            }
            chunksRef.current = [];
            mediaRecorderRef.current = null;
            setRecording(false);
            setStatus('⏹️ Stopped');
          }
        };

        // start recording
        mr.start();
        setRecording(true);
        setStatus('🎤 Listening...');
        setResult((r) => ({ ...r, transcript: 'Listening...' }));
      } catch (err) {
        console.error('Mic error:', err);
        setStatus('Microphone access denied');
        // cleanup any allocated stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
        mediaRecorderRef.current = null;
        setRecording(false);
      }
    } else {
      // STOP recording - only if recorder exists
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop();
        } else {
          // ensure tracks stopped even if recorder missing
          if (streamRef.current) {
            streamRef.current.getTracks().forEach((t) => t.stop());
            streamRef.current = null;
          }
          mediaRecorderRef.current = null;
          setRecording(false);
          setStatus('⏹️ Stopped');
        }
      } catch (err) {
        console.error('Error stopping recorder:', err);
        setStatus('Error stopping recorder');
        setRecording(false);
      }
    }
  };

  // cleanup if component unmounts
  useEffect(() => {
    return () => {
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop();
        }
      } catch (e) { /* ignore */ }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, []);

  return (
    <Page title="🎤 Real-Time Listening" subtitle="Record, transcribe, and detect sentiment in real time">
      <div className="grid-realtime">

        {/* Controller - full width */}
        <div className="col controller">
          <Card title="Controller" subtitle="Start/Stop and status">
            <div className="row">
              <button className="btn" onClick={toggleRecording}>
                {recording ? 'Stop Listening' : 'Start Listening'}
              </button>
              <span className="muted">Status: {status}</span>
            </div>
            <div style={{ marginTop: 12 }}>
              <p><b>Transcript:</b> {result.transcript}</p>
              <p><b>Sentiment:</b> {result.sentiment}</p>
              <p><b>Tone:</b> {result.tone}</p>
              <p><b>Date:</b> {result.date}</p>
            </div>
          </Card>
        </div>

        {/* Quick Tips - left bottom */}
        <div className="col tips">
          <Card title="Quick Tips" subtitle="Live coaching">
            <ul style={{ margin: '6px 0 0 18px' }}>
              <li>Mirror customer tone; keep sentences short.</li>
              <li>If negative, acknowledge and propose one clear next step.</li>
              <li>Use open questions to uncover use-case and urgency.</li>
            </ul>
          </Card>
        </div>

        {/* Why Sentiment - right bottom */}
        <div className="col why">
          <Card title="📝 Why this sentiment?" subtitle="Explanation">
            <p>{result.explanation || 'Waiting for input...'}</p>
          </Card>
        </div>
      </div>
    </Page>
  );
}
