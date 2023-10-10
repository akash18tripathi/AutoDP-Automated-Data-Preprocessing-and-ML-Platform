import './App.css';
import React, { useState } from "react";
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';

import Login from './Login';
import CommonPage from './CommonPage';
import Register from './Register';
import FileUpload from './Form';

function App(){
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // const toggleLoginStatus = () => {
  //   setIsLoggedIn(!isLoggedIn);
  // };
  
  // return (
  //   <Router>
  //     <div className="App">
  //       <h1>Welcome to Your App</h1>
  //       <button onClick={toggleLoginStatus}>
  //         {isLoggedIn ? 'Logout' : 'Login/Register'}
  //       </button>

  //       <Switch>
  //         <Route path="/" exact>
  //           {isLoggedIn ? <Redirect to="/dashboard" /> : <h2>Please login or register.</h2>}
  //         </Route>
  //         <Route path="/login">
  //           {isLoggedIn ? <Redirect to="/dashboard"/> : <Login isLoggedIn={isLoggedIn} toggleLoginStatus={toggleLoginStatus} />}
  //         </Route>
  //         <Route path="/register">
  //           {isLoggedIn ? <Redirect to="/dashboard" /> : <Register />}
  //         </Route>
  //         <Route path="/dashboard">
  //           {isLoggedIn ? <FileUpload /> : <Redirect to="/" />}
  //         </Route>
  //       </Switch>
  //     </div>
  //   </Router>
  // );

  return (
    <div>
      {/* {isLoggedIn ? <FileUpload /> : <Login setIsLoggedIn={setIsLoggedIn}></CommonPage>} */}
      {isLoggedIn ? <FileUpload /> : <Login setIsLoggedIn={setIsLoggedIn}></Login>}
      {/* <FileUpload></FileUpload> */}
    
     </div>
  );
}

export default App;
