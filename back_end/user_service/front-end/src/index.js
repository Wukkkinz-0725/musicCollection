import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import Homepage from "./Homepage";
import Login from './Login';
import Register from './Register'
import Mainpage from './Mainpage'
import {Routes, Route, Router, BrowserRouter, Switch, useNavigate} from 'react-router-dom';

class IndexPage extends React.Component {

  render() {
    return (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/Login" element={<Login />} />
            <Route path="/Register" element={<Register />} />
            <Route path="/Main" element={<Mainpage />} />
          </Routes>
        </BrowserRouter>
    );
  }
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<IndexPage />);
