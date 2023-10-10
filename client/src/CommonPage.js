import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LoginPage from './Login';
import RegisterPage from './Register';

function CommonPage({setIsLoggedIn}) {
  return (
    <Router>
      {/* <Switch> */}
        <Route exact path="/" render={() => <LoginPage setIsLoggedIn={setIsLoggedIn} />} />
        <Route path="/register" component={RegisterPage} />
      {/* </Switch> */}
    </Router>
  );
}

export default CommonPage;
