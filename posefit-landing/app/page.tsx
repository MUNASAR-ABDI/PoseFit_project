'use client';

import AppCard from '@/components/AppCard';
import { AssistantIcon, TrainerIcon } from '@/components/Icons';

export default function Home() {
  return (
    <main style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '2rem',
      background: 'linear-gradient(135deg, #0f0320 0%, #1e1132 50%, #2a1447 100%)',
      position: 'relative',
      overflow: 'hidden',
      color: '#f0f0ff',
      transition: 'background 0.3s ease, color 0.3s ease'
    }}>
      {/* Theme Toggle - hidden since we're using only dark theme */}
      {/* <ThemeToggle /> */}

      {/* Background elements for visual appeal */}
      <div style={{
        position: 'absolute',
        width: '400px',
        height: '400px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(106, 38, 205, 0.2) 0%, rgba(106, 38, 205, 0) 70%)',
        top: '-100px',
        right: '-100px',
        zIndex: 0
      }} />
      
      <div style={{
        position: 'absolute',
        width: '300px',
        height: '300px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0) 70%)',
        bottom: '-50px',
        left: '-50px',
        zIndex: 0
      }} />

      {/* Logo and Title Section */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginTop: '2rem',
        zIndex: 1
      }}>
        <div style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          backgroundColor: '#7747dc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.5rem',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
          border: '3px solid #ffd700'
        }}>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="60" 
            height="60" 
            viewBox="0 0 24 24" 
            fill="none"
            stroke="#ffd700" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path>
            <line x1="4" y1="22" x2="4" y2="15"></line>
          </svg>
        </div>
        
        <h1 style={{ 
          fontSize: '3.5rem', 
          fontWeight: 'bold', 
          margin: '0 0 1rem 0',
          background: 'linear-gradient(90deg, #ffd700, #ffecb3)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textAlign: 'center'
        }}>
          Welcome to PoseFit
        </h1>
        
        <p style={{ 
          fontSize: '1.4rem', 
          color: '#b09acf', 
          marginBottom: '3rem',
          maxWidth: '600px',
          textAlign: 'center',
          lineHeight: '1.6'
        }}>
          Your comprehensive fitness ecosystem powered by AI
        </p>
      </div>

      {/* Service Cards */}
      <div style={{ 
        display: 'flex', 
        gap: '3rem',
        flexWrap: 'wrap',
        justifyContent: 'center',
        maxWidth: '1200px',
        zIndex: 1
      }}>
        {/* PoseFit Assistant Card */}
        <AppCard 
          title="PoseFit Assistant"
          description="Your personal AI fitness coach providing customized workout plans, nutrition advice, and real-time guidance."
          features={[
            'Personalized fitness plans', 
            'AI workout generation', 
            'Progress tracking'
          ]}
          accentColor="linear-gradient(90deg, #6a26cd, #8547e9)"
          buttonText="Open Assistant"
          icon={<AssistantIcon />}
          url="https://munasar-abdi.github.io/PoseFit_assistant/"
        />
        
        {/* PoseFit Trainer Card */}
        <AppCard 
          title="PoseFit Trainer"
          description="Real-time exercise analysis with pose detection technology to ensure proper form and maximize results."
          features={[
            'Form correction', 
            'Rep counting', 
            'Video recording & feedback'
          ]}
          accentColor="linear-gradient(90deg, #6a26cd, #8547e9)"
          buttonText="Start Training"
          icon={<TrainerIcon />}
          url="https://munasar-abdi.github.io/PoseFit_Trainer/"
        />
      </div>

      {/* Footer with additional information */}
      <div style={{
        marginTop: '4rem',
        borderTop: '1px solid #2d2040',
        paddingTop: '2rem',
        textAlign: 'center',
        width: '100%',
        maxWidth: '800px',
        zIndex: 1
      }}>
        <p style={{
          fontSize: '1rem',
          color: '#9a84c9',
          lineHeight: '1.6',
          marginBottom: '1rem'
        }}>
          Each application runs independently but works together as part of the PoseFit ecosystem.
          Start with either app and enhance your fitness journey today!
        </p>
        
        <div style={{
          fontSize: '0.875rem',
          color: '#8071a5',
          marginTop: '1rem'
        }}>
          © {new Date().getFullYear()} PoseFit - Revolutionizing fitness with AI
        </div>
      </div>
    </main>
  );
}