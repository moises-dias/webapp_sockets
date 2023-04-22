import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

function App() {
  const [message, setMessage] = useState("");
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io('http://192.168.59.100:30886');
    setSocket(newSocket);
    return () => newSocket.disconnect();
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on('new_point', data => {
      console.log(data);
      setMessage(`User ${data.user} clicked on (${data.x}, ${data.y})`);
    });

    return () => socket.off('new_point');
  }, [socket]);

  const handleClick = (e) => {
    if (!socket) return;

    const position = { x: e.clientX, y: e.clientY };
    socket.emit('click', position);
  };

  return (
    <div onClick={handleClick}>
      <h1>Hello World!!!</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;