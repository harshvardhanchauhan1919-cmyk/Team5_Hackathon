/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { isBreakMode } from '../breakMode';
import { Sidebar } from './Sidebar';
import { Menu, ShoppingCart, LogOut } from 'lucide-react';

export const Header: React.FC = () => {
  const { cart, currentPage, setPageView, user, isNavigating, logout } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
  const cartLinkSelector = isBreakMode('cart_selector') ? 'cart-link-v2' : 'shopping-cart-link';

  const handleCartClick = () => {
    setPageView('cart');
  };

  const handleHomeClick = () => {
    setPageView('inventory');
  };

  // Visual user has misaligned layouts
  const isVisualUser = user === 'visual_user';
  const headerClass = isVisualUser
    ? 'flex-col md:flex-row items-start md:items-end justify-between p-4 bg-yellow-50 border-b-4 border-yellow-400'
    : 'items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-xs';

  const logoClass = isVisualUser
    ? 'text-5xl font-mono text-pink-600 font-bold -skew-x-12 tracking-widest leading-none rotate-1'
    : 'text-2xl font-black tracking-tighter text-gray-900 uppercase cursor-pointer select-none';

  return (
    <>
      <header className={`relative flex z-40 shadow-xs ${headerClass}`}>
        {/* Left: Burger Menu Button */}
        <div className={`flex items-center gap-3 ${isVisualUser ? 'ml-12 mb-2' : ''}`}>
          <button
            id="react-burger-menu-btn"
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 hover:text-slate-800 transition-colors focus:outline-none"
            title="Open Menu"
          >
            <Menu className="h-6 w-6" />
          </button>

          {/* User profile tag */}
          {user && (
            <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100 font-mono">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
              {user}
            </span>
          )}
        </div>

        {/* Center: Brand Logo */}
        <div className={`${isVisualUser ? 'self-center my-4 ml-6' : ''}`}>
          <h2 id="logo-text" onClick={handleHomeClick} className={logoClass}>
            Swag Labs{isVisualUser ? ' ⚠️' : ''}
          </h2>
        </div>

        {/* Right: Cart Container */}
        <div id="shopping_cart_container" className={`flex items-center gap-4 ${isVisualUser ? 'mr-20' : ''}`}>
          {isNavigating && (
            <div className="flex items-center gap-1 text-slate-400 text-xs font-mono mr-2">
              <div className="h-3 w-3 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              <span>lagging...</span>
            </div>
          )}

          <button
            id="shopping_cart_link"
            data-test={cartLinkSelector}
            onClick={handleCartClick}
            className="relative p-2.5 rounded-xl hover:bg-slate-50 text-slate-600 hover:text-emerald-500 transition-all duration-150 focus:outline-none cursor-pointer"
            title="Shopping Cart"
          >
            <ShoppingCart className="h-6 w-6" />
            {cartCount > 0 && (
              <span
                data-test="shopping-cart-badge"
                className="shopping_cart_badge absolute top-1 right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white animate-scale-in"
              >
                {cartCount}
              </span>
            )}
          </button>

          {user && (
            <button
              id="logout_header_link"
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-250 text-gray-600 hover:text-red-600 hover:bg-red-50 hover:border-red-100 text-xs font-bold transition-all duration-150 focus:outline-none cursor-pointer"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          )}
        </div>
      </header>

      {/* Slide-out Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    </>
  );
};
