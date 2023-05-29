import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import backgroundImageSource from './background.png';
import playerImageSource from './player.png';
import bulletImageSource from './bullet.png';
import deadPlayerImageSource from './deadPlayer.png';

const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const CANVAS_BORDER_STYLE = '1px solid black';
const MOVEMENT_KEYS = [87, 83, 65, 68];

const backgroundImage = new Image();
const playerImage = new Image();
const bulletImage = new Image();
const deadPlayerImage = new Image();

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
  // TODO block commands if player is dead
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [lastAngle, setLastAngle] = useState(0);
  const [mouseCursor, setMouseCursor] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const usersRef = useRef(users);
  useEffect(() => {
    usersRef.current = users;
  }, [users]);

  const mouseCursorRef = useRef(mouseCursor);
  useEffect(() => {
    mouseCursorRef.current = mouseCursor;
  }, [mouseCursor]);

  const drawCanvas = (context) => {
    context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    context.drawImage(backgroundImage, 0, 0);
  };

  const drawPlayers = (context, users) => {
    for (let i = 0; i < users.length; i++) {
      // const angle = Math.atan2(mouseCursor.y - users[i].y, mouseCursor.x - users[i].x);
      context.save();
      context.translate(users[i].x, users[i].y);
      context.rotate(users[i].angle + Math.PI / 2);
      // starting at -15 and width of 30.
      // add if type == player or type == bullet
      // to change the image and size
      if (users[i].type === 'player') {
        if (users[i].alive === 'yes') {
          context.drawImage(playerImage, -15, -15, 30, 30);
        }
        else {
          context.drawImage(deadPlayerImage, -15, -15, 30, 30);
        }
      }
      else if (users[i].type === 'bullet') {
        context.drawImage(bulletImage, -10, -10, 20, 20);
      }

      context.restore();
      // TODO add if entity = player before drawing its name
      if (users[i].type === 'player') {
        context.fillText(users[i].name, users[i].x - 20, users[i].y + 5);
      }
    }
  };

  const drawRestartMessage = (context, player) => {
    if (player.alive != 'yes') {
      
      const text1 = 'Killed by ---';
      const text2 = 'Press ENTER to restart';

      context.font = 'bold 30px sans-serif';
      context.fillStyle = 'blue';

      const text1Width = context.measureText(text1).width;
      const text2Width = context.measureText(text2).width;
      const centerX1 = 200 - (text1Width / 2);
      const centerX2 = 200 - (text2Width / 2);

      //context.textBaseline = 'middle';

      context.fillText(text1, centerX1, 200);
      context.fillText(text2, centerX2, 240);
      context.font = '10px sans-serif';
      context.fillStyle = '#000000';
    }
  };

  const drawShadows = (context, player) => {
    // TODO draw shadows on fixed places (walls)
    player.shadow.forEach(shadow => {
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
    // const newSocket = io('http://192.168.1.2:5000', { query: { name: userName} });
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

  // handle mouse click
  useEffect(() => {
    if (!socket) return;

    const handleClick = (event) => {
      if (event.button === 0) {
        const player = usersRef.current.find(item => item.name === userName);
        if (player === undefined) {
          console.log("PLAYER UNDEFINED");
          return;
        }
        const angle = Math.atan2(mouseCursorRef.current.y - player.y, mouseCursorRef.current.x - player.x);
        socket.emit('left_click', { x: player.x, y: player.y, angle: angle });
      }
    };

    window.addEventListener('mousedown', handleClick);

    return () => {
      window.removeEventListener('mousedown', handleClick);
    };
  }, [socket]);

  // handle backend socket messages
  useEffect(() => {
    if (!socket) return;

    socket.on('update_entities', users => {
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
      if (MOVEMENT_KEYS.includes(event.keyCode)) {
        socket.emit('start_moving', { direction: event.keyCode });
      }
    };
    
    // TODO pressing A,S,D then releasing A,S,D will trigger new key pressing
    // of D when releasing A and S
    // POSSIBLE SOLUTION: store a list with pressed keys?
    const handleKeyRelease = (event) => {
      if (MOVEMENT_KEYS.includes(event.keyCode)) {
        socket.emit('stop_movement', { direction: event.keyCode });
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
    if (!isImageLoaded) return;

    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    drawCanvas(context);
    drawPlayers(context, users);

    const player = users.find(item => item.name === userName);
    if (player === undefined) {
      console.log("PLAYER UNDEFINED");
      return;
    }

    const angle = Math.atan2(mouseCursorRef.current.y - player.y, mouseCursorRef.current.x - player.x);
    if (Math.abs(angle - lastAngle) > 0.5) {
      // TODO set a minimum interval between these messages?
      setLastAngle(angle)
      socket.emit('update_angle', { angle: angle });
    }

    drawShadows(context, player);
    drawRestartMessage(context, player);

    return () => {};
  }, [isImageLoaded, users]);

  // draw when user move the MOUSE
  useEffect(() => {
    if (!isImageLoaded) return;

    // TODO keep track of player instead of finding it all the time
    // and set a minimum intervall, maybe 100ms, between each
    // call of this function
    // maybe set a lastMouseCursor (x, y) and call the function only if
    // current - last mouse cursor in x and y is greater than a threshold
    const player = usersRef.current.find(item => item.name === userName);
    if (player === undefined) {
      console.log("PLAYER UNDEFINED");
      return;
    }
    const angle = Math.atan2(mouseCursor.y - player.y, mouseCursor.x - player.x);
    if (Math.abs(angle - lastAngle) > 0.5) {
      // TODO set a minimum interval between these messages?
      setLastAngle(angle)
      socket.emit('update_angle', { angle: angle });
    }

    return () => {};
  }, [mouseCursor]);

  // load images
  useEffect(() => {
    // TODO improve this logic to load images in paralel
    backgroundImage.src = backgroundImageSource;
    backgroundImage.onload = () => {
      playerImage.src = playerImageSource;
      playerImage.onload = () => {
        bulletImage.src = bulletImageSource;
        bulletImage.onload = () => {
          deadPlayerImage.src = deadPlayerImageSource;
          deadPlayerImage.onload = () => {
            setIsImageLoaded(true);
          }
        }
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
