import React, { useState } from 'react';
import { useNavigate, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import RegisterPage from './Register';

const LoginPage = ({ setIsLoggedIn }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');


  const handleSubmit = async (e) => {
    e.preventDefault();
    let uri='/login';
    console.log(username);
    console.log(password);
    axios.post(uri, {
        username: username,
        password: password,
      })
      .then(res => {
        console.log(res);
        if(res.data.message === 'Login successful'){
            console.log('Login Sucess!!!');
            setIsLoggedIn(true);
        }else{
            console.log('Login failed');
            setIsLoggedIn(false);
        }
        
      })
      .catch(error => {
        console.log('Login failed');
      });
    
  };

//   const registerPage=()=>{
//     navigate('/register');
//   }

  return (
    <div>
      <h2>Login</h2>
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
        <button type="submit">Login</button>

      </form>
      {/* <p>Don't have an account? <button onClick={registerPage}>Register here</button></p> */}
    </div>
  );
};

export default LoginPage;
