import React, { useState } from "react";
import ReactDOM from "react-dom";
import { useNavigate, useHistory } from "react-router-dom";
import checkLogin from "./checkLogin.js"

import "./Homepage.css"

function Homepage() {
  const navigate = useNavigate();

  function onButtonClick() {
    var requestOptions = {
      method: "GET",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
    };
    checkLogin(navigate, requestOptions);
  }
  
    return (
      <div className="welcome">
        <p>Welcome to the music collection website!</p>
        <p>Your personal music collection.</p>
        <button onClick={onButtonClick} className="goButton">
          Let's Go!
        </button>
      </div>
    );
}

export default Homepage;
