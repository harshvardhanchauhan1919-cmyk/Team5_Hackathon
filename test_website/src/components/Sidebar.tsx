/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useApp } from '../context/AppContext';
import { X, LayoutGrid, Info, LogOut, RotateCcw } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user, logout, resetState, setPageView, selectProduct } = useApp();

  const handleAllItems = () => {
    selectProduct(null);
    setPageView('inventory');
    onClose();
  };

  const handleAbout = (e: React.MouseEvent) => {
    e.preventDefault();
    onClose();
    alert(
      "About Sauce Demo Clone:\n\nThis is a high-fidelity replica of the original SauceLabs Swag Labs website, built using modern React, TypeScript, and Tailwind CSS.\n\nCreated primarily for testing automated scripts (Selenium, Playwright, Cypress) and training developers on handling e-commerce workflows and user simulation edge cases."
    );
  };

  const handleLogout = () => {
    logout();
    onClose();
  };

  const handleReset = () => {
    resetState();
    onClose();
    alert('Application state has been reset successfully!');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-sans">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Slideout Container */}
      <div className="absolute inset-y-0 left-0 max-w-full flex">
        <div className="w-80 max-w-sm bg-gray-950 text-white flex flex-col shadow-2xl relative">
          {/* Header section with Close Button */}
          <div className="flex justify-between items-center px-6 py-5 border-b border-gray-800">
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tighter text-white uppercase">Swag Labs</span>
              {user && <span className="text-[10px] text-gray-400 font-mono mt-0.5">{user}</span>}
            </div>
            <button
              id="react-burger-cross-btn"
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors focus:outline-none"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Links list */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {/* All Items */}
            <button
              id="inventory_sidebar_link"
              onClick={handleAllItems}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold text-gray-200 hover:text-white hover:bg-gray-800/80 rounded-lg transition-all duration-150 text-left cursor-pointer"
            >
              <LayoutGrid className="h-4 w-4 text-emerald-500" />
              All Items
            </button>

            {/* About */}
            <a
              id="about_sidebar_link"
              href="https://saucelabs.com/"
              onClick={handleAbout}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold text-gray-200 hover:text-white hover:bg-gray-800/80 rounded-lg transition-all duration-150 text-left cursor-pointer"
            >
              <Info className="h-4 w-4 text-emerald-500" />
              About
            </a>

            {/* Reset App State */}
            <button
              id="reset_sidebar_link"
              onClick={handleReset}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold text-gray-200 hover:text-white hover:bg-gray-800/80 rounded-lg transition-all duration-150 text-left cursor-pointer"
            >
              <RotateCcw className="h-4 w-4 text-emerald-500" />
              Reset App State
            </button>

            {/* Separator */}
            <div className="border-t border-gray-800 my-4" />

            {/* Logout */}
            <button
              id="logout_sidebar_link"
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-all duration-150 text-left cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </nav>

          {/* Footer inside sidebar */}
          <div className="p-6 border-t border-gray-800 text-[10px] text-gray-500 font-mono">
            <p>SWAG LABS CLONE v1.1</p>
            <p className="mt-1">Environment: QA Stable</p>
          </div>
        </div>
      </div>
    </div>
  );
};
