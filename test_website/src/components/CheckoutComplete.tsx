/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { isBreakMode } from '../breakMode';
import { ShoppingBag, Sparkles, CheckCircle2 } from 'lucide-react';

export const CheckoutComplete: React.FC = () => {
  const { resetState, setPageView, selectProduct, user } = useApp();

  // Reset the cart state when this page mounts (completed order clears items)
  useEffect(() => {
    resetState();
  }, []);

  const handleBackHome = () => {
    selectProduct(null);
    setPageView('inventory');
  };

  const isVisualUser = user === 'visual_user';
  const completeHeaderSelector = isBreakMode('complete_selector') ? 'order-complete-title' : 'complete-header';
  const containerClass = isVisualUser
    ? 'flex items-start bg-pink-100 p-24 font-mono rotate-12 border-4 border-yellow-500'
    : 'max-w-xl mx-auto py-12 px-6 font-sans';

  return (
    <div className={`min-h-screen bg-gray-50/50 flex items-center justify-center ${containerClass}`} id="checkout_complete_container">
      <div className={isVisualUser ? '' : 'w-full max-w-md mx-auto bg-white p-8 md:p-10 shadow-xs border border-gray-200 rounded-xl text-center flex flex-col items-center'}>
        {/* Animated Badge */}
        <div className="relative mb-6">
          <div className="h-16 w-16 bg-emerald-50 border border-emerald-100 rounded-full flex items-center justify-center text-emerald-500 shadow-inner">
            <CheckCircle2 className="h-8 w-8 animate-scale-in" />
          </div>
          <div className="absolute -top-1 -right-1 bg-amber-400 text-white p-1 rounded-full animate-bounce">
            <Sparkles className="h-3 w-3" />
          </div>
        </div>

        {/* Complete Step title */}
        <div className="mb-4">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
            Order Dispatched Successfully
          </div>
          <h2 className="text-xl md:text-2xl font-black text-gray-900 tracking-tight" data-test="title">
            Checkout: Complete!
          </h2>
        </div>

        {/* Primary headers */}
        <h3 data-test={completeHeaderSelector} className="complete-header text-sm font-bold text-gray-800 mt-2">
          Thank you for your order!
        </h3>

        <p className="complete-text text-gray-400 text-xs leading-relaxed mt-1 mb-8 max-w-xs mx-auto">
          Your order has been dispatched, and will arrive shortly with our Free Pony Express delivery squad!
        </p>

        {/* Return Button */}
        <button
          id="back-to-products"
          data-test="back-to-products"
          onClick={handleBackHome}
          className="w-full py-3 bg-gray-900 hover:bg-emerald-600 text-white font-bold rounded-lg text-xs shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer flex items-center justify-center gap-2"
        >
          <ShoppingBag className="h-4 w-4" />
          Back Home
        </button>
      </div>
    </div>
  );
};
