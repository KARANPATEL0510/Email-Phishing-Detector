import React, { useState } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-hot-toast';  // Import toast

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    // Check if both email and new password fields are filled
    if (!email || !newPassword) {
      setError('Please fill in all fields.');
      return;
    }

    try {
      // Log data being sent for debugging
      console.log('Sending data:', { email, new_password: newPassword });

      const response = await axios.post('http://localhost:5000/forgot-password', { email, new_password: newPassword });

      // Log response for debugging
      console.log('Response:', response);

      // If the response is successful
      if (response.status === 200) {
        setMessage('Password reset successful.');
        toast.success('Password reset successful.');  // Success toast
        setTimeout(() => navigate('/'), 3000); // Redirect after 3s
      }
    } catch (err) {
      // Log the error for debugging
      console.error('Error during password reset:', err);
      setError(err.response?.data?.error || 'Failed to reset password.');
      toast.error(err.response?.data?.error || 'Failed to reset password.');  // Error toast
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-times font-semibold text-center mb-6">Forgot Password</h2>
        {error && <p className="text-red-500 text-center mb-4">{error}</p>}
        {message && <p className="text-green-500 text-center mb-4">{message}</p>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:border-indigo-500"
              placeholder="Enter your email"
              required
            />
          </div>
          <div className="mb-4 relative">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newPassword">
              New Password
            </label>
            <div className="relative">
              <input
                id="newPassword"
                type={showPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:border-indigo-500 pr-12"
                placeholder="Enter a new password"
                required
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="absolute inset-y-0 right-2 flex items-center px-2 cursor-pointer"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
            </div>
          </div>
          <button
            type="submit"
            className="w-full bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-indigo-600 transition duration-300"
          >
            Reset Password
          </button>
        </form>
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">Remembered your password?</p>
          <a href="/" className="text-sm text-indigo-500 hover:underline">
            Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;