import React from 'react';
import "./index.css"
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Route, Routes, BrowserRouter } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import App from './App';

const Root = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
    </Routes>
  </BrowserRouter>
);
const rootElement = document.getElementById('root'); // Ensure you have a div with id="root" in your HTML
const root = ReactDOM.createRoot(rootElement);
root.render(<Root />);
