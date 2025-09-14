import React from "react";
import { Link } from "react-router-dom";
import "./Header.css";

function Header() {
  return (
    <header className="header">
      <h1 className="logo">🎤 AI Sales Assistant</h1>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/listening">Real-Time Listening</Link>
        <Link to="/analysis">Smart Analysis</Link>
        <Link to="/suggestions">AI Suggestions</Link>
      </nav>
    </header>
  );
}

export default Header;
