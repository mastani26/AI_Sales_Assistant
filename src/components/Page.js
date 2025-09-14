import React from 'react';

export default function Page({ title, subtitle, children }) {
  return (
    <div className="container">
      <div className="hero">
        <h1 style={{margin:'0 0 6px', fontSize:28}}>{title}</h1>
        {subtitle && <p className="muted" style={{margin:0}}>{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
