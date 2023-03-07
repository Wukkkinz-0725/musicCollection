import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import "./Register.css";

function Register() {
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
        navigate("/Login");
      }
      else {
        // navigate("/Something")
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
      "password": formData[1].value,
      "email": formData[2].value
    };

    console.log(data);

    const requestOptions = {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    fetch("http://localhost:9001/v1/users/register", requestOptions)
      .then((response) => handleResponse(response))
      .catch((error) => handleError(error));
  };

  // Not removing this for now, can be used for fomatting check later
  const renderErrorMessage = (name) =>
    name === errorMessages.name && (
      <div className="error">{errorMessages.message}</div>
    );

  // JSX code for login form
  const renderForm = (
    <div>
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
        <div className="input-container">
          <label>Email </label>
          <input type="text" name="pass" required />
          {renderErrorMessage("email")}
        </div>
        <div className="button-container">
          <input type="submit" />
        </div>
      </form>
      </div>
    </div>
  );

  return (
    <div className="app">
      <div className="title">
      <p> Don't have an account? </p>
      <p> Sign up first before log in!</p>
      </div>
      <div className="register-form">
        <div className="title">Sign Up</div>
        {renderForm}
      </div>
    </div>
  );
}

export default Register;
