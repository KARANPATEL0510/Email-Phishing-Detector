import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';  
import Login from './components/login';
import Register from './components/registration';
import ForgotPassword from './components/forgot_password';
import Main from './components/Main_page'; 

function App() {
  return (
    <Router>
      <div>
        {/* Toaster will display all toast notifications */}
        <Toaster position="top-center" />  
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/main" element={<Main />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
