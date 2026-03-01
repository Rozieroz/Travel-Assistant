import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ChatProvider } from './contexts/ChatContext';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Chat from './pages/Chat';
import './styles/globals.css';

export default function App() {
  return (
    <BrowserRouter>
      <ChatProvider>
        <Routes>
          <Route
            path="/"
            element={
              <Layout overlay="light">
                <Landing />
              </Layout>
            }
          />
          <Route
            path="/chat"
            element={
              <Layout overlay="dark">
                <Chat />
              </Layout>
            }
          />
        </Routes>
      </ChatProvider>
    </BrowserRouter>
  );
}
