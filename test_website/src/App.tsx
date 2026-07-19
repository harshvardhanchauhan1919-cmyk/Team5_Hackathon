/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Header } from './components/Header';
import { LoginView } from './components/LoginView';
import { InventoryList } from './components/InventoryList';
import { InventoryItemDetail } from './components/InventoryItemDetail';
import { CartView } from './components/CartView';
import { CheckoutStepOne } from './components/CheckoutStepOne';
import { CheckoutStepTwo } from './components/CheckoutStepTwo';
import { CheckoutComplete } from './components/CheckoutComplete';
import { TestingPanel } from './components/TestingPanel';
import { Loader2 } from 'lucide-react';

const AppContent: React.FC = () => {
  const { user, currentPage, isNavigating } = useApp();

  // If the user isn't logged in, or we are on the login page, render the Login view
  if (!user || currentPage === 'login') {
    return (
      <div className="relative min-h-screen bg-slate-50">
        <LoginView />
        <TestingPanel />
      </div>
    );
  }

  // Render main application layout for logged-in sessions
  return (
    <div className="relative min-h-screen bg-slate-50/30 flex flex-col justify-between selection:bg-emerald-500/20 selection:text-emerald-800">
      {/* Top persistent Navigation Bar */}
      <Header />

      {/* Main active viewport */}
      <main className="flex-grow relative">
        {/* Full-Page Spinner Overlay for Performance Glitch simulated lag */}
        {isNavigating && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-xs z-50 flex flex-col items-center justify-center gap-3">
            <Loader2 className="h-10 w-10 text-emerald-500 animate-spin" />
            <p className="text-xs font-semibold text-slate-500 font-mono tracking-wider">
              [Simulation Delay] Loading testing endpoints...
            </p>
          </div>
        )}

        {/* Dynamic page switcher router */}
        {(() => {
          switch (currentPage) {
            case 'inventory':
              return <InventoryList />;
            case 'details':
              return <InventoryItemDetail />;
            case 'cart':
              return <CartView />;
            case 'checkout-1':
              return <CheckoutStepOne />;
            case 'checkout-2':
              return <CheckoutStepTwo />;
            case 'checkout-complete':
              return <CheckoutComplete />;
            default:
              return <InventoryList />;
          }
        })()}
      </main>

      {/* Testing console floating overlay */}
      <TestingPanel />
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

