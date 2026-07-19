/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { LogIn, Key, User, ShieldAlert } from 'lucide-react';

export const LoginView: React.FC = () => {
  const { login } = useApp();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await login(username.trim(), password.trim());
      if (!result.success) {
        setError(result.error || 'An unknown error occurred');
      }
    } catch (err: any) {
      setError(err?.message || 'Server Exception: Auth route failure');
    } finally {
      setIsLoading(false);
    }
  };

  const autofillCredentials = (user: string) => {
    setUsername(user);
    setPassword('secret_sauce');
    setError(null);
  };

  return (
    <div id="login_container" className="min-h-screen bg-gray-50 flex flex-col justify-between p-4 md:p-8 font-sans">
      {/* Visual Accent */}
      <div className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-gray-800 to-gray-950" />

      {/* Header Logo */}
      <div className="flex justify-center mt-8 md:mt-12">
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-gray-900 uppercase select-none flex items-center gap-1">
          <span>Swag Labs</span>
          <span className="text-emerald-500 font-bold">.</span>
        </h1>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-md mx-auto my-6 bg-white shadow-xs rounded-xl border border-gray-200 overflow-hidden transition-all duration-300">
        <div className="p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-lg font-bold text-gray-800 tracking-tight">Welcome Back</h2>
            <p className="text-xs text-gray-400 mt-1 font-medium">Please sign in to your testing profile to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Input */}
            <div className="space-y-1">
              <label htmlFor="user-name" className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  id="user-name"
                  data-test="username"
                  type="text"
                  placeholder="Username"
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 focus:bg-white transition-all duration-150 shadow-2xs"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-1">
              <label htmlFor="password" className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Key className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  id="password"
                  data-test="password"
                  type="password"
                  placeholder="Password"
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 focus:bg-white transition-all duration-150 shadow-2xs"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Error Message Box */}
            {error && (
              <div
                data-test="error"
                className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2.5 animate-pulse"
              >
                <ShieldAlert className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-xs font-bold text-red-700 leading-tight">{error}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-600 font-bold text-sm focus:outline-none shrink-0"
                >
                  &times;
                </button>
              </div>
            )}

            {/* Login Button */}
            <button
              id="login-button"
              data-test="login-button"
              type="submit"
              className="w-full py-3 bg-gray-900 hover:bg-gray-800 text-white font-bold rounded-lg flex items-center justify-center gap-2 shadow-xs transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              <LogIn className="h-4 w-4" />
              {isLoading ? 'Signing In...' : 'Login'}
            </button>
          </form>
        </div>
      </div>

      {/* Informative Credentials Guide (The real saucedemo has this at the bottom) */}
      <div className="w-full max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-5 rounded-xl border border-gray-200 shadow-2xs mt-4 text-xs">
        <div id="login_credentials" className="space-y-2 border-r border-gray-200 pr-0 md:pr-4">
          <h3 className="font-bold text-gray-800 text-sm flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-gray-900" />
            Accepted Usernames:
          </h3>
          <div className="grid grid-cols-2 gap-1 font-mono text-gray-600">
            {[
              'standard_user',
              'locked_out_user',
              'problem_user',
              'performance_glitch_user',
              'visual_user',
              'error_user',
            ].map((usr) => (
              <button
                key={usr}
                onClick={() => autofillCredentials(usr)}
                className="text-left py-1 px-1.5 hover:bg-gray-50 border border-transparent hover:border-gray-200 rounded text-[11px] font-semibold transition-colors cursor-pointer text-emerald-600"
                title="Click to autofill"
              >
                {usr}
              </button>
            ))}
          </div>
        </div>

        <div id="password_credentials" className="space-y-2 pl-0 md:pl-4 flex flex-col justify-start">
          <h3 className="font-bold text-gray-800 text-sm flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Password for all users:
          </h3>
          <p className="font-mono text-gray-600 bg-gray-50 p-2 rounded border border-gray-200 inline-block font-semibold self-start">
            secret_sauce
          </p>
          <p className="text-[10px] text-gray-400 mt-2 leading-relaxed">
            Note: Toggle usernames to simulate different network speeds, broken UI renderings, blocked items, or validation error alerts.
          </p>
        </div>
      </div>

      {/* Footer credits */}
      <div className="text-center text-[11px] text-gray-400 mt-8 mb-2">
        <p>© 2026 Swag Labs. Designed for high-fidelity QA & automated software testing simulation.</p>
      </div>
    </div>
  );
};
