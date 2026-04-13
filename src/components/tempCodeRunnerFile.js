import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx';

const FraudDetector = () => {
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [savedResults, setSavedResults] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const handleInputChange = (e) => {
    setWebsiteUrl(e.target.value);
  };

  const handleCheckClick = async () => {
    if (!websiteUrl.trim()) {
      setError('Please enter a URL.');
      setMessage('');
    } else {
      setError('');
      try {
        const response = await fetch('http://localhost:5000/check-website', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: websiteUrl }),
        });
        const data = await response.json();
        
        if (response.status === 450) {
          setMessage(data.message);
          setError(''); 
        } else if (response.status === 400) {
          setError(data.message);
          setMessage(''); 
        }
        
      } catch (error) {
        setError('Error checking the website. Please try again.');
        setMessage(''); 
      }
    }
  };

  const handleSaveClick = () => {
    if (websiteUrl && (message || error)) {
      const now = new Date();
      const currentDate = now.toLocaleDateString();
      const currentTime = now.toLocaleTimeString();
      const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' });
      const currentYear = now.getFullYear();

      setSavedResults((prev) => [
        ...prev,
        { 
          url: websiteUrl, 
          message: message || error, 
          srNo: prev.length + 1, 
          date: currentDate,
          time: currentTime,
          day: currentDay,
          year: currentYear 
        },
      ]);
      setMessage(''); 
      setError(''); 
    } else {
      setError('Please check a website before saving.');
    }
  };

  const handleGenerateSpreadsheet = () => {
    if (savedResults.length === 0) {
      alert('No data to export!');
      return;
    }

    const worksheet = XLSX.utils.json_to_sheet(
      savedResults.map(({ srNo, url, message, date, time, day, year }) => ({ 
        SrNo: srNo, 
        URL: url, 
        Status: message, 
        Date: date,
        Time: time,
        Day: day,
        Year: year
      }))
    );
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Fraud Results');

    XLSX.writeFile(workbook, 'fraud_results.xlsx');
  };

  const toggleMenu = () => {
    setMenuOpen((prev) => !prev);
  };

  const handleClickOutside = useCallback(
    (e) => {
      if (menuOpen && menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    },
    [menuOpen]
  );

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleClickOutside]);

  const handleMenuItemClick = () => {
    setMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 p-4 relative">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-white text-2xl font-semibold">Fraud Detector</h1>
          {/* <div className="flex-1 flex justify-center">
            <span className="text-white text-xl font-semibold">Mini Project</span>
          </div> */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-white focus:outline-none"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16m-7 6h7"
                ></path>
              </svg>
            </button>
          </div>
          <div
            ref={menuRef}
            className={`fixed top-0 left-0 w-full h-full bg-blue-600 md:bg-transparent md:relative md:w-auto md:h-auto md:flex md:items-center md:justify-between ${
              menuOpen ? 'block' : 'hidden'
            }`}
          >
<div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0">

              <a
                href="#home"
                className="text-white hover:text-gray-300 p-4"
                onClick={handleMenuItemClick}
              >
                Home
              </a>
              <a
                href="#about"
                className="text-white hover:text-gray-300 p-4"
                onClick={handleMenuItemClick}
              >
                About Us
              </a>
              <a
                href="#contact"
                className="text-white hover:text-gray-300 p-4"
                onClick={handleMenuItemClick}
              >
                Contact Us
              </a>
              <Link
                to="/"
                className="text-white hover:text-gray-300 p-4"
                onClick={handleMenuItemClick}
              >
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div id="home" className="bg-gray-100 py-10 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Welcome to our FRAUD DETECTOR
          </h2>
          <h3 className="text-lg md:text-xl mb-6">CHECK THE WEBSITE HERE</h3>

          <div className="max-w-lg mx-auto">
            <input
              type="text"
              value={websiteUrl}
              onChange={handleInputChange}
              placeholder="Enter website URL"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring focus:ring-blue-500"
            />
            {error && <p className="text-red-500 mt-2">{error}</p>}
            {message && <p className="text-green-500 mt-2">{message}</p>}

            <div className="flex justify-center mt-4 space-x-4">
              <button
                onClick={handleCheckClick}
                className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700"
              >
                Check
              </button>
              <button
                onClick={handleSaveClick}
                className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700"
              >
                Save
              </button>
              <button
                onClick={handleGenerateSpreadsheet}
                className="bg-yellow-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-yellow-700"
              >
                Spreadsheet
              </button>
            </div>
          </div>
        </div>
      </div>

      <div id="about" className="bg-gray-100 py-10 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">About Us</h2>
          <p className="text-lg text-gray-700 mb-4 max-w-3xl mx-auto">
            Hi we are code carbon, students of Xaviers Institute of Engineering.
            We are like-minded students with a keen interest in the field of cybersecurity and networking.
            We present our very first topic as a whole that is "Fraud Website Detector," which will notify
            us of various suspicious websites and which parts of them are suspicious.
            We developed this project using React.js for the front end and Python Flask for the back end.
            Hope you like it.
          </p>
        </div>
      </div>

      <div id="contact" className="bg-gray-100 py-10 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-6">Contact Us</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <img
                src="https://i.pinimg.com/736x/5f/40/6a/5f406ab25e8942cbe0da6485afd26b71.jpg"
                alt="Justin Fernandes"
                className="mx-auto w-32 h-32 rounded-full mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Justin Fernandes</h3>
              <div className="flex justify-center space-x-4">
                <a
                  href="https://in.linkedin.com/in/justin-fernandes-848459247"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img
                    src="https://static.vecteezy.com/system/resources/previews/012/660/862/non_2x/linkedin-logo-on-transparent-isolated-background-free-vector.jpg"
                    alt="LinkedIn"
                    className="w-8 h-8"
                  />
                </a>
                <a href="mailto:justin.fds2005@gmail.com">
                  <img
                    src="https://img.freepik.com/premium-vector/mail-icon-vector_942802-576.jpg"
                    alt="Mail"
                    className="w-8 h-8"
                  />
                </a>
              </div>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <img
                src="https://i.pinimg.com/736x/5f/40/6a/5f406ab25e8942cbe0da6485afd26b71.jpg"
                alt="Gracian Lopes"
                className="mx-auto w-32 h-32 rounded-full mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Gracian Lopes</h3>
              <div className="flex justify-center space-x-4">
                <a
                  href="https://www.linkedin.com/in/gracian-lopes/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img
                    src="https://static.vecteezy.com/system/resources/previews/012/660/862/non_2x/linkedin-logo-on-transparent-isolated-background-free-vector.jpg"
                    alt="LinkedIn"
                    className="w-8 h-8"
                  />
                </a>
                <a href="mailto:gracian.lopes@gmail.com">
                  <img
                    src="https://img.freepik.com/premium-vector/mail-icon-vector_942802-576.jpg"
                    alt="Mail"
                    className="w-8 h-8"
                  />
                </a>
              </div>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <img
                src="https://i.pinimg.com/736x/5f/40/6a/5f406ab25e8942cbe0da6485afd26b71.jpg"
                alt="Shaikh Hassan"
                className="mx-auto w-32 h-32 rounded-full mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Shaikh Hassan</h3>
              <div className="flex justify-center space-x-4">
                <a
                  href="https://www.linkedin.com/in/hassan-shaikh-3a055b21a"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img
                    src="https://static.vecteezy.com/system/resources/previews/012/660/862/non_2x/linkedin-logo-on-transparent-isolated-background-free-vector.jpg"
                    alt="LinkedIn"
                    className="w-8 h-8"
                  />
                </a>
                <a href="mailto:shaikh.hassan1024@gmail.com">
                  <img
                    src="https://img.freepik.com/premium-vector/mail-icon-vector_942802-576.jpg"
                    alt="Mail"
                    className="w-8 h-8"
                  />
                </a>
              </div>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <img
                src="https://i.pinimg.com/736x/5f/40/6a/5f406ab25e8942cbe0da6485afd26b71.jpg"
                alt="Zaid Ansari"
                className="mx-auto w-32 h-32 rounded-full mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Zaid Ansari</h3>
              <div className="flex justify-center space-x-4">
                <a
                  href="https://www.linkedin.com/in/zaid-ansari-977155319?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img
                    src="https://static.vecteezy.com/system/resources/previews/012/660/862/non_2x/linkedin-logo-on-transparent-isolated-background-free-vector.jpg"
                    alt="LinkedIn"
                    className="w-8 h-8"
                  />
                </a>
                <a href="mailto:zaidnansari2011@gmail.com">
                  <img
                    src="https://img.freepik.com/premium-vector/mail-icon-vector_942802-576.jpg"
                    alt="Mail"
                    className="w-8 h-8"
                  />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FraudDetector;