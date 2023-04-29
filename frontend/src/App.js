import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import backgroundImage from './background.png';

const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const CANVAS_BORDER_STYLE = '1px solid black';
const CIRCLE_RADIUS = 50;
const MOVEMENT_KEYS = [87, 83, 65, 68];

const image = new Image();

function App() {
  const [socket, setSocket] = useState(null);
  const [users, setUsers] = useState([]);
  const [shadows, setShadows] = useState([]);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const canvasRef = useRef(null);

  const userName = (Math.floor(Math.random() * (9999 - 1000 + 1)) + 1000).toString();

  const drawCanvas = (context, users) => {
    context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    context.drawImage(image, 0, 0);
    for (let i = 0; i < users.length; i++) {
      context.beginPath();
      context.arc(users[i].x, users[i].y, CIRCLE_RADIUS, 0, 2 * Math.PI, false);
      context.fillStyle = '#FF4136';
      context.fill();
      context.fillStyle = '#000';
      context.font = 'bold 20px sans-serif';
      context.fillText(users[i].user, users[i].x - 20, users[i].y + 5);
    }
    
    shadows.forEach(shadow => {
      context.beginPath();
      shadow.forEach(point => {
        context.lineTo(point[0], point[1]);
      });
      context.closePath();
    
      context.fillStyle = 'black';
      context.fill();
      context.stroke();
    });
    

  };
  useEffect(() => {
    const newSocket = io('http://localhost:5000', { query: { name: userName} });
    setSocket(newSocket);
    return () => newSocket.disconnect();
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on('update_users', users => {
      setUsers(users);
    });

    socket.on('update_shadow', shadows => {
      setShadows(shadows);
    });

    return () => {
      socket.off('update_users');
      socket.off('update_shadow');
    };
  }, [socket]);

useEffect(() => {
  if (!socket) return;

  let intervalId;
  let activeKeys = [];

  const handleKeyDown = (keyCode) => {
    if (MOVEMENT_KEYS.includes(keyCode)) {
      socket.emit('move', { user: userName, direction: keyCode });
    }
  };

  const handleKeyPress = (event) => {
    if (event.repeat) return;
    const index = activeKeys.indexOf(event.keyCode);
    if (index > -1) {
      return;
    }
    activeKeys.push(event.keyCode);
    if (intervalId) {
      return;
    }
    intervalId = setInterval(() => {
      activeKeys.forEach(keyCode => handleKeyDown(keyCode));
    }, 50);

    console.log(intervalId)
  };

  const handleKeyRelease = (event) => {
    const index = activeKeys.indexOf(event.keyCode);
    if (index > -1) {
      activeKeys.splice(index, 1);
    }
    if (activeKeys.length === 0) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };

  document.addEventListener('keydown', handleKeyPress);
  document.addEventListener('keyup', handleKeyRelease);

  return () => {
    document.removeEventListener('keydown', handleKeyPress);
    document.removeEventListener('keyup', handleKeyRelease);
  };
}, [socket]);

  useEffect(() => {
    if (!isImageLoaded) {
      return;
    }
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    drawCanvas(context, users);
    return () => {};
  }, [isImageLoaded, users]);

  useEffect(() => {
    image.src = backgroundImage;
    image.onload = () => {
      setIsImageLoaded(true);
      console.log('Image loaded!');
    };
    console.log("foo")
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{ border: CANVAS_BORDER_STYLE }}></canvas>
    </div>
  );
}

export default App;