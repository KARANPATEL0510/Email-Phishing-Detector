import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import toast, { Toaster } from "react-hot-toast";

const PhishingDetector = () => {
  const [url, setUrl] = useState("");
  const [emailContent, setEmailContent] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleCheck = async () => {
    setError("");
    setResult(null);
    setLoading(true);

    if (!url && !emailContent) {
      setError("Please enter a URL or email content.");
      toast.error("Please enter a URL or email content.");
      setLoading(false);
      return;
    }

    try {
      const apiUrl = "http://127.0.0.1:5000/api/check";
      const response = await axios.post(apiUrl, { url, emailContent });

      if (response.data && response.data.message) {
        setResult(response.data);

        if (response.data.message.includes("Phishing")) {
          toast.error("Phishing detected!");
        } else {
          toast.success("No phishing detected!");
        }
      } else {
        throw new Error("Unexpected response format");
      }
    } catch (err) {
      setError("Error checking the input. Please try again.");
      toast.error("Error checking the input. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToSection = (id) => {
    const section = document.getElementById(id);
    if (section) {
      section.scrollIntoView({ behavior: "smooth" });
      setMenuOpen(false);
    }
  };

  const contacts = [
    { name: "Anuj Suvarna", email: "anujsuvarna7@gmail.com" },
    { name: "Simran Busi", email: "honey040304@gmail.com" },
    { name: "Justin Fernandes", email: "justin.fds2005@example.com" },
    { name: "Karan Patel", email: "karanp24680@gmail.com" },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-100">
      <nav className="w-full bg-indigo-500 text-white p-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto px-4">
          <h1 className="text-xl font-bold">Email Phishing Detector</h1>

          <div className="hidden md:flex space-x-6">
            <Link to="/" className="hover:underline">Home</Link>
            <button onClick={() => scrollToSection("about-section")} className="hover:underline">
              About
            </button>
            <button onClick={() => scrollToSection("contact-section")} className="hover:underline">
              Contact
            </button>
          </div>

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-2xl focus:outline-none"
            aria-label="Toggle navigation menu"
          >
            {menuOpen ? "✖" : "☰"}
          </button>
        </div>

        {menuOpen && (
          <div className="md:hidden flex flex-col mt-2 space-y-2 bg-indigo-400 p-3 rounded">
            <Link to="/" className="hover:underline" onClick={() => setMenuOpen(false)}>Home</Link>
            <button onClick={() => scrollToSection("about-section")} className="hover:underline text-left">
              About
            </button>
            <button onClick={() => scrollToSection("contact-section")} className="hover:underline text-left">
              Contact
            </button>
          </div>
        )}
      </nav>

      <div className="w-full max-w-md bg-white p-6 mt-16 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-indigo-500 mb-4">
          Email Phishing Detector
        </h1>

        <input
          type="text"
          placeholder="Enter website URL (e.g., https://example.com)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="border p-2 rounded w-full mb-4"
        />

        <textarea
          placeholder="Paste email content or suspicious links here..."
          value={emailContent}
          onChange={(e) => setEmailContent(e.target.value)}
          className="border p-2 rounded w-full h-32 mb-4"
        />

        <button
          onClick={handleCheck}
          className="w-full bg-indigo-500 hover:bg-indigo-700 text-white p-2 rounded flex justify-center items-center"
          disabled={loading}
        >
          {loading ? "Checking..." : "Check"}
        </button>

        {error && <p className="text-red-500 mt-2 text-center">{error}</p>}
        {result && <p className="text-green-500 mt-2 text-center">{result.message}</p>}
      </div>

      <div id="about-section" className="w-full max-w-2xl bg-white p-6 mt-8 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-indigo-500 text-center mb-4">About</h2>
        <p className="text-gray-700 text-center">
          Welcome to our <b>Email Phishing Detector</b>! This tool is designed to analyze emails and detect 
          potential phishing attempts. Whether it's a suspicious <b>URL</b> or <b>email content</b>, our system is built to help you stay safe from scams.
        </p>
        <p className="text-gray-700 text-center mt-3">
          Simply enter the email text or link, and we'll scan it for <b>phishing indicators</b> such as 
          fraudulent domains, suspicious wording, and more!
        </p>
      </div>

      <div id="contact-section" className="w-full max-w-4xl bg-white p-6 mt-8 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-indigo-500 text-center mb-4">Contact Us</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {contacts.map((contact, index) => (
            <div key={index} className="bg-indigo-100 p-4 rounded-lg shadow flex flex-col items-center">
              <img 
                src="https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvdjkzNy1hZXctMTY1LWtsaGN3ZWNtLmpwZw.jpg"
                alt="Contact"
                className="w-24 h-24 rounded-full mb-3"
              />
              <h3 className="text-lg font-semibold text-indigo-600">{contact.name}</h3>
              <a 
                href={`mailto:${contact.email}`} 
                className="text-blue-500 underline mt-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                {contact.email}
              </a>
            </div>
          ))}
        </div>
      </div>

      <Toaster />
    </div>
  );
};

export default PhishingDetector;