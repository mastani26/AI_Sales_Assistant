import React from "react";
import "./AISuggestions.css";

function AISuggestions() {
  return (
    <div className="suggestions-container">
      <h2>💡 AI Suggestions</h2>

      <div className="suggestion-box">
        <h3>Improve Engagement</h3>
        <ul>
          <li>Ask open-ended questions to keep the conversation flowing.</li>
          <li>Mirror the customer's tone to build rapport.</li>
          <li>Keep responses concise and focused on customer needs.</li>
        </ul>
      </div>

      <div className="suggestion-box">
        <h3>Sales Strategy Prompts</h3>
        <ul>
          <li>“Have you considered how this feature fits into your current workflow?”</li>
          <li>“What’s your main goal with this solution?”</li>
          <li>“Would you like to explore a premium tier with weightier benefits?”</li>
        </ul>
      </div>

      <div className="suggestion-box">
        <h3>Objection Handling</h3>
        <ul>
          <li>“I understand your concern. Let me offer an alternative that addresses that.”</li>
          <li>“That’s a valid point — here’s how we avoid that issue.”</li>
          <li>“Would you like to see pricing flexibility or additional support options?”</li>
        </ul>
      </div>

      <div className="suggestion-box">
        <h3>Post-Call Follow-ups</h3>
        <ul>
          <li>“Thanks for your time! I’ll summarize next steps in an email within the hour.”</li>
          <li>“Any questions still lingering that I can clarify now?”</li>
          <li>“How would you feel about a quick demo of the solution tailored to your scenario?”</li>
        </ul>
      </div>

    </div>
  );
}

export default AISuggestions;
