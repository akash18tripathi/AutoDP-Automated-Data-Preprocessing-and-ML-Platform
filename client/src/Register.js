import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const RegisterPage = ({ history }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    let uri='http://localhost:5000/register'
    axios.post(uri, {
        username: username,
        password: password,
      })
      .then(res => {
        setMessage(res.data.message);
        history.push('/login');
      })
      .catch(error => {
        console.log('Registration failed');
      });
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Register</button>
      </form>
      <p>{message}</p>
      <p>Already have an account? <Link to="/login">Login here</Link></p>
    </div>
  );
};

export default RegisterPage;
