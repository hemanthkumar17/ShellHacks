import { useState } from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Question from "./components/Questions";
import Landing from "./components/Landing";
import Learn from "./components/Learn";
import Particles from "react-tsparticles";
import particlesConfig from "./config/particlesConfig";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/quiz" element={<Question />} />
        <Route path="/learn" element={<Learn />} />
      </Routes>
    </Router>
  );
}

export default App;
