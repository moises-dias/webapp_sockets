import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/")
      .then(res => res.text())
      .then(setMessage);
  }, []);

  useEffect(() => {
    const socket = io('http://localhost:5000');
    
    const handleMouseMove = (e) => {
      const { clientX, clientY } = e;
      socket.emit('mousemove', { x: clientX, y: clientY });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      socket.disconnect();
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div>
      <h1>Hello, World!</h1>
      <p>{message}</p>
      <p>test</p>
    </div>
  );
}

export default App;