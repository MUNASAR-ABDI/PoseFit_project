'use client';

import React from 'react';
import Link from 'next/link';

interface AppCardProps {
  title: string;
  description: string;
  features: string[];
  accentColor: string;
  buttonText: string;
  icon: React.ReactNode;
  url: string;
}

function isInternalUrl(url: string) {
  return url.startsWith('/');
}

export default function AppCard({
  title,
  description,
  features,
  accentColor,
  buttonText,
  icon,
  url
}: AppCardProps) {
  return (
    <div 
      style={{
        background: '#191628',
        borderRadius: '1.5rem',
        padding: '2rem',
        width: '350px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease',
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
        border: '1px solid #2d2040'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = 'translateY(-10px)';
        e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5)';
        e.currentTarget.style.borderColor = '#ffd700';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)';
        e.currentTarget.style.borderColor = '#2d2040';
      }}
    >
      {/* Accent color bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '8px',
        background: accentColor
      }} />
      
      {/* Icon container */}
      <div style={{ marginBottom: '1.5rem' }}>
        {icon}
      </div>
      
      <h2 style={{ 
        fontSize: '1.8rem', 
        fontWeight: 'bold', 
        marginBottom: '1rem',
        color: '#f0f0ff'
      }}>
        {title}
      </h2>
      
      <p style={{
        fontSize: '1.1rem',
        color: '#b09acf',
        marginBottom: '2rem',
        textAlign: 'center',
        lineHeight: '1.6'
      }}>
        {description}
      </p>
      
      <ul style={{
        listStyle: 'none',
        padding: 0,
        margin: '0 0 2rem 0',
        width: '100%'
      }}>
        {features.map((feature, index) => (
          <li key={index} style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '0.75rem',
            fontSize: '1rem',
            color: '#d4c9e9'
          }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffd700" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '0.75rem' }}>
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            {feature}
          </li>
        ))}
      </ul>
      
      {isInternalUrl(url) ? (
        <Link href={url} legacyBehavior>
          <a style={{
            padding: '0.75rem 1.5rem',
            background: '#6a26cd',
            color: 'white',
            borderRadius: '0.75rem',
            fontSize: '1.1rem',
            fontWeight: 'semibold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            transition: 'background 0.3s ease',
            textDecoration: 'none',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = '#8547e9';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = '#6a26cd';
          }}
          >
            {buttonText}
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: '0.5rem' }}>
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </a>
        </Link>
      ) : (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            padding: '0.75rem 1.5rem',
            background: '#6a26cd',
            color: 'white',
            borderRadius: '0.75rem',
            fontSize: '1.1rem',
            fontWeight: 'semibold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            transition: 'background 0.3s ease',
            textDecoration: 'none',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = '#8547e9';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = '#6a26cd';
          }}
        >
          {buttonText}
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: '0.5rem' }}>
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </a>
      )}
    </div>
  );
} 