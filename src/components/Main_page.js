import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import toast, { Toaster } from "react-hot-toast";

const axiosInstance = axios;

const PhishingDetector = () => {
  const [activeTab, setActiveTab] = useState("content"); // "url", "content", or "email_id"
  const [contentType, setContentType] = useState("Email Content"); // for "content" tab
  const [url, setUrl] = useState("");
  const [emailContent, setEmailContent] = useState("");
  const [emailId, setEmailId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const response = await axiosInstance.get("http://localhost:5000/api/history");
      if (response.data && response.data.success) {
        setHistory(response.data.history);
      }
    } catch (err) {
      console.error("Error fetching scan history:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleCheck = async () => {
    setError("");
    setResult(null);
    setLoading(true);

    if (activeTab === "url" && !url) {
      setError("Please enter a URL to check.");
      toast.error("Please enter a URL to check.");
      setLoading(false);
      return;
    }
    if (activeTab === "content" && !emailContent) {
      setError("Please enter text content to check.");
      toast.error("Please enter text content.");
      setLoading(false);
      return;
    }
    if (activeTab === "email_id" && !emailId) {
      setError("Please enter an Email ID to check.");
      toast.error("Please enter an Email ID.");
      setLoading(false);
      return;
    }

    try {
      const apiUrl = "http://127.0.0.1:5000/api/check";
      let payload;
      if (activeTab === "url") {
        payload = { url, contentType: "Website URL" };
      } else if (activeTab === "email_id") {
        payload = { emailId, contentType: "Email ID Check" };
      } else {
        payload = { emailContent, contentType };
      }

      const response = await axiosInstance.post(apiUrl, payload);

      if (response.data && response.data.success) {
        setResult(response.data);
        fetchHistory(); // refresh history list

        const risk = response.data.overall_risk;
        if (risk.level.includes("High")) {
          toast.error("High Risk Detected!");
        } else if (risk.level.includes("Suspicious")) {
          toast.error("Suspicious Content Detected!"); // using toast.error for warning visibility
        } else {
          toast.success("Safe/Low Risk Content.");
        }
      } else {
        throw new Error("Unexpected response format");
      }
    } catch (err) {
      setError("Error checking the input. Please ensure the backend server is running.");
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
    <div className="min-h-screen flex flex-col items-center bg-gray-50">
      <nav className="w-full bg-indigo-600 text-white p-4 shadow-md sticky top-0 z-50">
        <div className="flex items-center justify-between max-w-6xl mx-auto px-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🛡️</span>
            <h1 className="text-xl font-extrabold tracking-tight">Email Phishing & AI Detector</h1>
          </div>

          <div className="hidden md:flex space-x-6 items-center">
            <Link to="/" className="hover:text-indigo-200 transition">Home</Link>
            <button onClick={() => scrollToSection("check-section")} className="hover:text-indigo-200 transition">
              Scanner
            </button>
            <button onClick={() => scrollToSection("history-section")} className="hover:text-indigo-200 transition">
              Scan History
            </button>
            <button onClick={() => scrollToSection("about-section")} className="hover:text-indigo-200 transition">
              About
            </button>
            <button onClick={() => scrollToSection("contact-section")} className="hover:text-indigo-200 transition">
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
          <div className="md:hidden flex flex-col mt-2 space-y-2 bg-indigo-500 p-3 rounded">
            <Link to="/" className="hover:underline" onClick={() => setMenuOpen(false)}>Home</Link>
            <button onClick={() => scrollToSection("check-section")} className="hover:underline text-left">Scanner</button>
            <button onClick={() => scrollToSection("history-section")} className="hover:underline text-left">Scan History</button>
            <button onClick={() => scrollToSection("about-section")} className="hover:underline text-left">About</button>
            <button onClick={() => scrollToSection("contact-section")} className="hover:underline text-left">Contact</button>
          </div>
        )}
      </nav>

      {/* Main Scanner Section */}
      <div id="check-section" className="w-full max-w-4xl px-4 mt-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Input Panel */}
          <div className="lg:col-span-7 bg-white p-6 rounded-2xl shadow-lg border border-gray-150">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🔍</span> Content Analyzer
            </h2>

            {/* Tab Navigation */}
            <div className="flex border-b border-gray-200 mb-6">
              <button
                className={`py-2 px-4 font-semibold text-sm border-b-2 transition-all ${
                  activeTab === "content"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => {
                  setActiveTab("content");
                  setResult(null);
                  setError("");
                }}
              >
                Email Detection
              </button>
              <button
                className={`py-2 px-4 font-semibold text-sm border-b-2 transition-all ${
                  activeTab === "url"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => {
                  setActiveTab("url");
                  setResult(null);
                  setError("");
                }}
              >
                Website URL
              </button>
              <button
                className={`py-2 px-4 font-semibold text-sm border-b-2 transition-all ${
                  activeTab === "email_id"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => {
                  setActiveTab("email_id");
                  setResult(null);
                  setError("");
                }}
              >
                Email ID Checker
              </button>
            </div>

            {activeTab === "content" && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">Content Category</label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="border border-gray-300 p-2.5 rounded-lg w-full mb-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-700 bg-white"
                >
                  <option value="Email Content">Email Body / Message</option>
                  <option value="IT Announcement">IT Department Alert / Announcement</option>
                  <option value="HR Notification">HR Announcement / Policy Update</option>
                </select>

                <label className="block text-sm font-medium text-gray-600 mb-2">Paste Content</label>
                <textarea
                  placeholder="Paste the email content, review, comment, or document text here (minimum 10 characters)..."
                  value={emailContent}
                  onChange={(e) => setEmailContent(e.target.value)}
                  className="border border-gray-300 p-3 rounded-lg w-full h-48 mb-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-800 text-sm"
                />
              </div>
            )}

            {activeTab === "url" && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">Website URL</label>
                <input
                  type="text"
                  placeholder="Enter website URL (e.g., https://secure-bank-login.xyz)"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="border border-gray-300 p-3 rounded-lg w-full mb-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-800 text-sm"
                />
              </div>
            )}

            {activeTab === "email_id" && (
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">Email ID to Check</label>
                <input
                  type="text"
                  placeholder="Enter sender email address (e.g., support@utiitsl-bank.xyz)"
                  value={emailId}
                  onChange={(e) => setEmailId(e.target.value)}
                  className="border border-gray-300 p-3 rounded-lg w-full mb-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-800 text-sm"
                />
              </div>
            )}

            <button
              onClick={handleCheck}
              className="w-full bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99] text-white p-3 rounded-xl font-bold shadow-md transition flex justify-center items-center text-base"
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Running Multi-Layer Analysis...
                </>
              ) : (
                "Scan Content"
              )}
            </button>

            {error && <p className="text-red-600 mt-3 text-center text-sm font-semibold">{error}</p>}
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-5">
            {result ? (
              <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-150 animate-fadeIn">
                <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">🛡️</span> Security Analysis Report
                </h2>

                {/* Risk status alert */}
                <div className={`p-4 rounded-xl mb-6 shadow-sm border ${
                  result.overall_risk.score > 80 
                    ? "bg-red-50 text-red-700 border-red-200"
                    : result.overall_risk.score > 60
                    ? "bg-orange-50 text-orange-850 border-orange-200"
                    : result.overall_risk.score > 40
                    ? "bg-amber-50 text-amber-800 border-amber-200"
                    : result.overall_risk.score > 20
                    ? "bg-blue-50 text-blue-800 border-blue-200"
                    : "bg-emerald-50 text-emerald-700 border-emerald-200"
                }`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs uppercase tracking-wider font-extrabold block opacity-85">Risk Status</span>
                    {result.overall_risk.flagged_for_review && (
                      <span className="bg-red-600 text-white font-extrabold text-[9px] px-2 py-0.5 rounded uppercase tracking-wider animate-pulse">
                        Audit Flagged
                      </span>
                    )}
                  </div>
                  <span className="text-lg font-bold block">{result.overall_risk.level}</span>
                  <p className="text-xs mt-1 leading-normal opacity-90">{result.overall_risk.description}</p>
                </div>

                {/* Score and Confidence */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-gray-50 border border-gray-150 p-3.5 rounded-xl text-center">
                    <span className="text-[10px] font-bold text-gray-500 uppercase block tracking-wider">Suspicion Score</span>
                    <span className={`text-2xl font-extrabold ${
                      result.overall_risk.score > 80 ? "text-red-600" : result.overall_risk.score > 40 ? "text-amber-500" : "text-emerald-600"
                    }`}>{result.overall_risk.score}%</span>
                  </div>
                  <div className="bg-gray-50 border border-gray-150 p-3.5 rounded-xl text-center">
                    <span className="text-[10px] font-bold text-gray-500 uppercase block tracking-wider">Confidence Level</span>
                    <span className="text-2xl font-extrabold text-indigo-600">{result.overall_risk.confidence_level}</span>
                  </div>
                </div>

                {/* Risk Summary */}
                <div className="mb-5 text-xs">
                  <span className="font-extrabold text-gray-700 block mb-1 uppercase tracking-wider text-[10px]">Risk Summary</span>
                  <p className="text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">{result.overall_risk.risk_summary}</p>
                </div>

                {/* Positive & Negative Indicators */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5 text-xs">
                  <div className="bg-emerald-50/50 border border-emerald-100 p-3 rounded-xl">
                    <span className="font-bold text-emerald-800 block mb-2 uppercase tracking-wider text-[10px]">✓ Positive Indicators</span>
                    <ul className="space-y-1.5 list-disc pl-4 text-gray-600">
                      {result.overall_risk.positive_indicators?.map((ind, idx) => (
                        <li key={idx} className="leading-tight text-[11px]">{ind}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-red-50/50 border border-red-100 p-3 rounded-xl">
                    <span className="font-bold text-red-800 block mb-2 uppercase tracking-wider text-[10px]">✗ Negative Indicators</span>
                    <ul className="space-y-1.5 list-disc pl-4 text-gray-650">
                      {result.overall_risk.negative_indicators?.map((ind, idx) => (
                        <li key={idx} className="leading-tight text-[11px]">{ind}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Recommendation */}
                <div className="mb-5 text-xs">
                  <span className="font-extrabold text-gray-700 block mb-1 uppercase tracking-wider text-[10px]">Security Recommendation</span>
                  <div className="bg-indigo-50 border border-indigo-100 p-3 rounded-lg flex items-start space-x-2">
                    <span className="text-base mt-0.5">💡</span>
                    <p className="text-indigo-900 font-medium leading-relaxed">{result.overall_risk.recommendation}</p>
                  </div>
                </div>

                {/* Contributing Factors Breakdown */}
                {result.overall_risk.factors && result.overall_risk.factors.length > 0 && (
                  <div className="mb-5 bg-gray-50 border border-gray-150 p-4 rounded-xl">
                    <span className="text-xs font-extrabold text-gray-500 block mb-3 uppercase tracking-wider">
                      Risk Weighting Details
                    </span>
                    <div className="space-y-2.5 max-h-48 overflow-y-auto pr-1">
                      {result.overall_risk.factors.map((factor, idx) => (
                        <div key={idx} className="flex justify-between items-start text-xs border-b border-gray-200 pb-2 last:border-0 last:pb-0">
                          <div className="pr-3">
                            <span className="font-bold text-gray-700 block">{factor.name}</span>
                            <span className="text-gray-500 text-[10px] block mt-0.5 leading-normal">{factor.reason}</span>
                          </div>
                          <span className="text-red-600 font-extrabold text-[11px] bg-red-50 px-1.5 py-0.5 rounded shrink-0">
                            +{factor.impact}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Important notice */}
                <div className="bg-gray-100 border border-gray-200 p-3.5 rounded-xl text-[10px] text-gray-500 leading-normal">
                  ⚠️ <strong>Rule Directive:</strong> Suspicion scores analyze semantic, stylometric, and domain records. AI and threat triggers flag items for security audit review; content blocks are not initiated automatically.
                </div>
              </div>
            ) : (
              <div className="bg-gray-100 border-2 border-dashed border-gray-300 p-10 rounded-2xl flex flex-col items-center justify-center text-center text-gray-500 h-full min-h-[350px]">
                <span className="text-4xl mb-3">📋</span>
                <h3 className="font-bold text-gray-700 text-base mb-1">Awaiting Content Scan</h3>
                <p className="text-xs max-w-xs leading-relaxed">
                  Enter a URL, email address, or paste text content on the left to perform phishing checks, linguistic variety checks, and similarity scans.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* History Feed Section */}
      <div id="history-section" className="w-full max-w-4xl px-4 mt-12 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-150">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center">
              <span className="mr-2">📜</span> Recent Audit Feed
            </h2>
            <button 
              onClick={fetchHistory}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 border border-indigo-200 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition"
            >
              Refresh Feed
            </button>
          </div>

          {history.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-500 font-semibold text-xs uppercase bg-gray-50">
                    <th className="p-3">Timestamp</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Content / Input</th>
                    <th className="p-3 text-center">AI generated</th>
                    <th className="p-3 text-right">Risk Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-gray-700">
                  {history.map((scan, idx) => {
                    const date = new Date(scan.timestamp);
                    const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
                    
                    return (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="p-3 text-xs whitespace-nowrap text-gray-500">
                          {dateStr}, {timeStr}
                        </td>
                        <td className="p-3">
                          <span className="bg-indigo-50 border border-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wide">
                            {scan.content_type || (scan.input_type === "url" ? "Website URL" : "Text")}
                          </span>
                        </td>
                        <td className="p-3 max-w-[200px] md:max-w-xs truncate text-xs font-mono text-gray-600">
                          {scan.input_data}
                        </td>
                        <td className="p-3 text-center font-bold">
                          <span className={scan.ai_analysis?.is_ai_generated ? "text-purple-600" : "text-gray-500"}>
                            {scan.ai_analysis?.ai_probability}%
                          </span>
                        </td>
                        <td className="p-3 text-right font-extrabold whitespace-nowrap">
                          <span className={`px-2.5 py-1 rounded-full text-[10px] tracking-wide uppercase ${
                            scan.overall_risk?.score > 75
                              ? "bg-red-100 text-red-800 border border-red-200"
                              : scan.overall_risk?.score > 40
                              ? "bg-amber-100 text-amber-800 border border-amber-200"
                              : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                          }`}>
                            {scan.overall_risk?.score}% {scan.overall_risk?.level.split(" ")[0]}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-400 text-sm">
              No recent audit logs found in the MongoDB `scans` collection. Run a scan above to start logging.
            </div>
          )}
        </div>
      </div>

      <div id="about-section" className="w-full max-w-4xl bg-white p-6 mt-6 rounded-2xl shadow-lg border border-gray-150">
        <h2 className="text-xl font-bold text-indigo-600 text-center mb-4 flex items-center justify-center">
          <span>ℹ️</span> About the System
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-600">
          <div className="leading-relaxed">
            <h3 className="font-bold text-gray-800 mb-2">Phishing Link & Domain Checker</h3>
            <p>
              Scans target websites for common automated phishing vectors, lookalike domain patterns, untrusted registrar extensions, and credential harvest templates to block access or flag risk instantly.
            </p>
          </div>
          <div className="leading-relaxed">
            <h3 className="font-bold text-gray-800 mb-2">Multi-Layer AI Content Recognition</h3>
            <p>
              Uses stylometric statistics (sentence length variances), linguistic patterns (TTR), semantic keywords, and historical fuzzy matching against previous campaigns in your database to trace machine-generated email bodies and alerts.
            </p>
          </div>
        </div>
      </div>

      <div id="contact-section" className="w-full max-w-4xl bg-white p-6 mt-8 rounded-2xl shadow-lg border border-gray-150 mb-16">
        <h2 className="text-xl font-bold text-indigo-600 text-center mb-6">Contact Support & Team</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {contacts.map((contact, index) => (
            <div key={index} className="bg-indigo-50 border border-indigo-100 p-4 rounded-xl flex flex-col items-center hover:shadow-md transition">
              <img 
                src="https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvdjkzNy1hZXctMTY1LWtsaGN3ZWNtLmpwZw.jpg"
                alt="Contact"
                className="w-16 h-16 rounded-full mb-3 shadow-inner object-cover"
              />
              <h3 className="text-xs font-bold text-gray-800 text-center leading-tight">{contact.name}</h3>
              <a 
                href={`mailto:${contact.email}`} 
                className="text-[10px] text-blue-600 underline mt-1 truncate max-w-full"
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