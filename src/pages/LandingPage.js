import React from "react";
import "./LandingPage.css";

function LandingPage() {
  return (
    <div className="landing">
      <div className="card">
        <h2>🎤 Real-Time Listening</h2>
        <p>
          Record, transcribe, and detect sentiment instantly with live coaching
          tips.
        </p>
      </div>

      <div className="card">
        <h2>📊 Smart Analysis</h2>
        <p>
          Analyze sentiment trends, visualize insights, and track customer tone
          over time.
        </p>
      </div>

      <div className="card">
        <h2>💡 AI Suggestions</h2>
        <p>
          Get contextual prompts and objection handling guidance for smoother
          conversations.
        </p>
      </div>
    </div>
  );
}

export default LandingPage;
