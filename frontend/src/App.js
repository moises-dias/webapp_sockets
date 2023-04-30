import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import backgroundImage from './background.png';
import playerImage from './player.png';

const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const CANVAS_BORDER_STYLE = '1px solid black';
const CIRCLE_RADIUS = 50;
const MOVEMENT_KEYS = [87, 83, 65, 68];

const image = new Image();
const userImage = new Image();

function InputScreen({ onSubmit }) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(inputValue);
  }

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Name:
          <input type="text" value={inputValue} onChange={handleInputChange} />
        </label>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

function App({ userName }) {
  const [socket, setSocket] = useState(null);
  const [users, setUsers] = useState([]);
  const [shadows, setShadows] = useState([]);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [mouseCursor, setMouseCursor] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const drawCanvas = (context) => {
    context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    context.drawImage(image, 0, 0);
  };

  const drawPlayers = (context, users) => {
    for (let i = 0; i < users.length; i++) {
      const angle = Math.atan2(mouseCursor.y - users[i].y, mouseCursor.x - users[i].x);
      context.save();
      context.translate(users[i].x, users[i].y);
      context.rotate(angle + Math.PI / 2);
      context.drawImage(userImage, -15, -15, 30, 30);
      context.restore();
      context.fillText(users[i].user, users[i].x - 20, users[i].y + 5);
    }
  };

  const drawSelf = (context, users) => {
    const player = users.find(item => item.user === userName);
    if (player === undefined) {
      console.log("PLAYER UNDEFINED");
      return;
    }
    const angle = Math.atan2(mouseCursor.y - player.y, mouseCursor.x - player.x);
    context.save();
    context.translate(player.x, player.y);
    context.rotate(angle + Math.PI / 2);
    context.drawImage(userImage, -15, -15, 30, 30);
    context.restore();
    context.fillText(player.user, player.x - 20, player.y + 5);
  };

  const drawShadows = (context) => {
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

  // connect to socket
  useEffect(() => {
    const newSocket = io('http://localhost:5000', { query: { name: userName} });
    setSocket(newSocket);
    return () => newSocket.disconnect();
  }, []);

  // update angle when mouse move
  useEffect(() => {
    const handleMouseMove = (event) => {
      setMouseCursor({ x: event.clientX, y: event.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  // handle backend socket messages
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

  // keyboard
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

  // draw when users or images are loaded
  useEffect(() => {
    if (!isImageLoaded) {
      return;
    }
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    drawCanvas(context);
    drawSelf(context, users);
    drawPlayers(context, users);
    drawShadows(context);
    return () => {};
  }, [isImageLoaded, users]);

  // draw when user move mouse
  useEffect(() => {
    if (!isImageLoaded) {
      return;
    }
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    drawSelf(context, users);
    return () => {};
  }, [mouseCursor]);

  // load images
  useEffect(() => {
    // TODO improve this logic to load images in paralel
    image.src = backgroundImage;
    image.onload = () => {
      userImage.src = playerImage;
      userImage.onload = () => {
        setIsImageLoaded(true);
      };
    };
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{ border: CANVAS_BORDER_STYLE }}></canvas>
    </div>
  );
}

function Main() {
  const [userName, setUserName] = useState(null);

  const handleSubmit = (value) => {
    setUserName(value);
  }

  return (
    <div>
      {userName ? <App userName={userName} /> : <InputScreen onSubmit={handleSubmit} />}
    </div>
  );
}

export default Main;