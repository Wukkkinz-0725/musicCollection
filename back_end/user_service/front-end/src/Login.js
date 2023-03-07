import React, { useState } from "react";
import { useNavigate } from "react-router-dom";


import "./Login.css";

function Login() {
  const navigate = useNavigate();

  // React States
  const [errorMessages, setErrorMessages] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);


  const errors = {
    uname: "invalid username",
    pass: "invalid password",
  };

  const handleResponse = (response) => {
    if (response.status === 200) {
        navigate("/Main");
      }
      else {
        // Error
      }
  }

  const handleError = (error) => {
    console.log(error);
  }

  const handleSubmit = (event) => {
    event.preventDefault();

    const formData = event.target.elements;
    const data = {
      "username": formData[0].value,
      "password": formData[1].value
    };

    console.log(data);

    const requestOptions = {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    fetch("http://localhost:9001/v1/users/login", requestOptions)
      .then((response) => handleResponse(response))
      .catch((error) => handleError(error));
  };

  // Generate JSX code for error message
  const renderErrorMessage = (name) =>
    name === errorMessages.name && (
      <div className="error">{errorMessages.message}</div>
    );

  // JSX code for login form
  const renderForm = (
    <div className="form">
      <form onSubmit={handleSubmit}>
        <div className="input-container">
          <label>Username </label>
          <input type="text" name="uname" required />
          {renderErrorMessage("uname")}
        </div>
        <div className="input-container">
          <label>Password </label>
          <input type="password" name="pass" required />
          {renderErrorMessage("pass")}
        </div>
        <div className="button-container">
          <input type="submit" />
        </div>
        <div className="sign-up">
          <label>Don't have an account?</label>
          <a href="/Register">Sign up</a>
        </div>
      </form>
    </div>
  );

  return (
    <div className="app">
      <div className="login-form">
        <div className="title">Sign In</div>
        {renderForm}
      </div>
    </div>
  );
}

export default Login;
