import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import LandingPage from "./pages/LandingPage";
import RealTimeListening from "./pages/RealTimeListening";
import SmartAnalysis from "./pages/SmartAnalysis";
import AISuggestions from "./pages/AISuggestions";
import "./index.css";

function App() {
  // Lift history state here
  const [history, setHistory] = useState([]);

  return (
    <Router>
      <Header />
      <Routes>
        <Route
          path="/"
          element={<LandingPage />}
        />
        <Route
          path="/listening"
          element={
            <RealTimeListening history={history} setHistory={setHistory} />
          }
        />
        <Route
          path="/analysis"
          element={<SmartAnalysis history={history} />}
        />
        <Route
          path="/suggestions"
          element={<AISuggestions />}
        />
      </Routes>
    </Router>
  );
}

export default App;
