import React from 'react';

export default function Card({ title, subtitle, children, right, className='' }) {
  return (
    <section className={`card ${className}`}>
      {(title || subtitle || right) && (
        <div className="row" style={{justifyContent:'space-between', marginBottom:12}}>
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="muted">{subtitle}</p>}
          </div>
          {right}
        </div>
      )}
      {children}
    </section>
  );
}
