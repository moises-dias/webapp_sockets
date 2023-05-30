import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import playerImageSource from './player.png';

const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const CANVAS_BORDER_STYLE = '1px solid black';

const playerImage = new Image();

function App({ userName }) {
  const [socket, setSocket] = useState(null);
  const [users, setUsers] = useState([]);
  // TODO block commands if player is dead
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const canvasRef = useRef(null);

  const drawPlayers = (context, users) => {
    for (let i = 0; i < users.length; i++) {
      context.save();
      context.translate(users[i].x, users[i].y);
      context.rotate(users[i].angle + Math.PI / 2);
      context.drawImage(playerImage, -15, -15, 30, 30);
      context.restore();
    }
  };


  // connect to socket
  useEffect(() => {
    const newSocket = io('http://localhost:5000', { query: { name: userName} });
    setSocket(newSocket);
    return () => newSocket.disconnect();
  }, []);

  // handle backend socket messages
  useEffect(() => {
    if (!socket) return;

    socket.on('update_entities', users => {
      console.log("received entities")
      setUsers(users);
    });

    return () => {
      socket.off('update_entities');
    };
  }, [socket]);

  // keyboard
  useEffect(() => {
    if (!socket) return;

    const handleKeyPress = (event) => {
      if (event.repeat) return;
      socket.emit('start_moving', { direction: event.keyCode });
    };
    
    const handleKeyRelease = (event) => {
      socket.emit('stop_movement', { direction: event.keyCode });
    };

    document.addEventListener('keydown', handleKeyPress);
    document.addEventListener('keyup', handleKeyRelease);

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
      document.removeEventListener('keyup', handleKeyRelease);
    };
  }, [socket, users]);

  // draw when users or images are loaded
  useEffect(() => {
    if (!isImageLoaded) return;

    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    drawPlayers(context, users);

    return () => {};
  }, [isImageLoaded, users]);


  // load images
  useEffect(() => {
    playerImage.src = playerImageSource;
    playerImage.onload = () => {
      setIsImageLoaded(true);
    };
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} width={CANVAS_WIDTH} height={CANVAS_HEIGHT} style={{ border: CANVAS_BORDER_STYLE }}></canvas>
    </div>
  );
}

function Main() {
  return (
    <div>
      <App userName={"test"} />
    </div>
  );
}

export default Main;
