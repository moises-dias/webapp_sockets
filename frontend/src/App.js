import React, { useState, useEffect } from 'react';

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/")
      .then(res => res.text())
      .then(setMessage);
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