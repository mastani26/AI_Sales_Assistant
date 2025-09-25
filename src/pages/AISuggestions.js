import React, { useState } from "react";
import "./AISuggestions.css";

export default function AISuggestions() {
  const [query, setQuery] = useState("");
  const [aiResponse, setAIResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Keyword-based heuristic for suggestions
  const cannedResponses = (q) => {
    const lower = (q || "").toLowerCase();
    const brands = [];

    // Footwear
    if (lower.includes("shoe") || lower.includes("sneaker") || lower.includes("running")) {
      brands.push("Nike", "Adidas", "Puma", "New Balance");
    }

    // Clothing / Fashion
    if (lower.includes("clo") || lower.includes("shirt") || lower.includes("pant") || lower.includes("jean") || lower.includes("fashion")) {
      brands.push("Zara", "H&M", "Uniqlo", "Levi's", "Mango");
    }

    // Luxury / Designer
    if (lower.includes("lux") || lower.includes("designer") || lower.includes("premium") || lower.includes("brand")) {
      brands.push("Gucci", "Prada", "Louis Vuitton", "Armani");
    }

    // Tech / Electronics
    if (lower.includes("tech") || lower.includes("phone") || lower.includes("laptop") || lower.includes("camera")) {
      brands.push("Apple", "Samsung", "OnePlus", "Sony");
    }

    // Hair / Skin / Beauty
    if (lower.includes("hair") || lower.includes("oil") || lower.includes("growth") || lower.includes("skin") || lower.includes("skincare")) {
      brands.push("Indulekha", "Kama Ayurveda", "Dabur Amla", "Himalaya Herbals", "Biotique");
    }

    // Food / Supplements
    if (lower.includes("protein") || lower.includes("nutrition") || lower.includes("vitamin")) {
      brands.push("MuscleBlaze", "Optimum Nutrition", "Herbalife", "GNC");
    }

    // Default fallback
    if (!brands.length) {
      brands.push("Nike", "Zara", "Levi's", "Apple", "Gucci");
    }

    const unique = Array.from(new Set(brands)).slice(0, 6);
    return `Based on your query, consider these brands: ${unique.join(", ")}.`;
  };

  const handleSubmit = () => {
    setError("");
    if (!query) {
      setError("Please enter a customer query.");
      return;
    }
    setLoading(true);
    try {
      const resp = cannedResponses(query);
      setAIResponse(resp);
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Try again.");
      setAIResponse("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="suggestions-container">
      <h2>💡 AI Sales Call Assistant — Quick Query</h2>

      <div className="ai-input-section">
        <input
          type="text"
          placeholder="Customer question (e.g. 'Which hair oils are best for growth?')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Processing..." : "Ask"}
        </button>
        {error && <p className="error">{error}</p>}
      </div>

      {aiResponse && (
        <div className="ai-response">
          <h3>AI Suggestions</h3>
          <p>{aiResponse}</p>
        </div>
      )}

      {/* ------------------ Offline suggestion boxes ------------------ */}
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
