// Layout.tsx ---  defines the main layout component for the application, which sets a full-screen background image with a gradient overlay to enhance readability. It accepts child components to render within this layout and allows for different overlay intensity options (light, medium, dark) to customize the visual appearance. The component is styled using inline styles and ensures that the content is displayed above the background and overlay layers.
import React from 'react';

const BG_IMAGE = 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=1920&q=85';

interface LayoutProps {
  children: React.ReactNode;
  overlay?: 'light' | 'medium' | 'dark';
}

export default function Layout({ children, overlay = 'medium' }: LayoutProps) {
  const overlayMap = {
    light: 'rgba(0,0,0,0.45)',
    medium: 'rgba(0,0,0,0.60)',
    dark: 'rgba(0,0,0,0.72)',
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundImage: `url(${BG_IMAGE})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        fontFamily: 'var(--font)',
      }}
    >
      {/* Gradient overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(
            to bottom,
            ${overlayMap[overlay]} 0%,
            rgba(0,0,0,0.55) 50%,
            rgba(0,0,0,0.75) 100%
          )`,
        }}
      />
      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1, height: '100%', width: '100%' }}>
        {children}
      </div>
    </div>
  );
}
