/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { UserType } from '../types';
import { Terminal, Settings, ChevronRight, RefreshCw, X, Play, Shield, Trash2 } from 'lucide-react';

export const TestingPanel: React.FC = () => {
  const {
    user,
    currentPage,
    cart,
    sortOption,
    checkoutInfo,
    consoleLogs,
    changeUserTypeDirectly,
    clearConsoleLogs,
    resetState,
  } = useApp();

  const [isOpen, setIsOpen] = useState(false);

  const userProfiles: { key: UserType; name: string; desc: string; color: string }[] = [
    {
      key: 'standard_user',
      name: 'Standard User',
      desc: 'Behaves normally with perfect item views and fast clicks.',
      color: 'bg-emerald-500 text-white',
    },
    {
      key: 'locked_out_user',
      name: 'Locked Out',
      desc: 'Immediate epic sadface login block upon password submission.',
      color: 'bg-red-600 text-white',
    },
    {
      key: 'problem_user',
      name: 'Problem User',
      desc: 'Corrupted item images, blocked cart clicks, locked sorting dropdown.',
      color: 'bg-amber-500 text-white',
    },
    {
      key: 'performance_glitch_user',
      name: 'Performance Glitch',
      desc: 'Simulates high api congestion; adds a 2.5s lag to every navigation.',
      color: 'bg-indigo-500 text-white',
    },
    {
      key: 'visual_user',
      name: 'Visual User',
      desc: 'Rotated and skewed borders, misaligned columns, out-of-bounds text.',
      color: 'bg-pink-500 text-white',
    },
    {
      key: 'error_user',
      name: 'Error User',
      desc: 'Simulates client-side exceptions; throws fatal alerts on checkout.',
      color: 'bg-rose-500 text-white',
    },
  ];

  return (
    <>
      {/* Floating QA Toggle Button */}
      <button
        id="qa-panel-toggle"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 z-50 p-3 bg-gray-900 hover:bg-gray-800 text-emerald-400 hover:text-emerald-300 font-bold rounded-full flex items-center gap-2 shadow-xl border border-gray-800 hover:scale-105 transition-all cursor-pointer font-sans"
        title="Open QA Test Controller"
      >
        <Settings className="h-5 w-5 animate-spin-slow" />
        <span className="text-xs font-semibold tracking-wider uppercase pr-1">QA Console</span>
      </button>

      {/* QA Panel Side Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end font-sans">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-gray-950/30 backdrop-blur-xs" onClick={() => setIsOpen(false)} />

          {/* Drawer Content */}
          <div className="relative w-full max-w-md bg-gray-900 text-gray-100 flex flex-col shadow-2xl border-l border-gray-800">
            {/* Drawer Header */}
            <div className="p-5 border-b border-gray-800 flex items-center justify-between bg-gray-950/50">
              <div className="flex items-center gap-2">
                <Terminal className="h-5 w-5 text-emerald-400" />
                <h3 className="font-extrabold text-sm uppercase tracking-wider text-gray-200">
                  QA Test Controller
                </h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Drawer Body - Scrollable */}
            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              {/* Profile Swapper Section */}
              <div className="space-y-3">
                <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                  <Shield className="h-3.5 w-3.5 text-indigo-400" />
                  Active Profile Simulator
                </h4>

                <div className="grid grid-cols-1 gap-2.5">
                  {userProfiles.map((p) => {
                    const isActive = user === p.key;
                    return (
                      <button
                        key={p.key}
                        id={`qa-switch-${p.key}`}
                        onClick={() => changeUserTypeDirectly(isActive ? null : p.key)}
                        className={`w-full p-3 rounded-lg border text-left flex items-start gap-3 transition-all duration-150 cursor-pointer ${
                          isActive
                             ? 'bg-gray-800 border-emerald-500 shadow-lg'
                             : 'bg-gray-950/40 border-gray-850 hover:bg-gray-800/30 hover:border-gray-700'
                        }`}
                      >
                        <div
                          className={`h-6 w-6 rounded-full shrink-0 flex items-center justify-center text-[10px] font-bold ${
                            isActive ? p.color : 'bg-gray-800 text-gray-400'
                          }`}
                        >
                          {isActive ? <Play className="h-3 w-3 fill-current" /> : p.key.slice(0, 2).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-gray-200">{p.name}</span>
                            {isActive && (
                              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 font-mono font-bold px-1.5 py-0.5 rounded border border-emerald-500/20">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <p className="text-[10px] text-gray-400 mt-1 leading-normal">{p.desc}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Telemetry States */}
              <div className="space-y-3">
                <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                  <Settings className="h-3.5 w-3.5 text-emerald-400" />
                  Live App Telemetry
                </h4>

                <div className="bg-gray-950 rounded-lg border border-gray-800 p-4 space-y-2 text-xs font-mono">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Current Page:</span>
                    <span className="text-emerald-400 font-semibold">{currentPage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Current User:</span>
                    <span className="text-blue-400 font-semibold">{user || 'logged_out'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Cart Count:</span>
                    <span className="text-amber-400 font-semibold">
                      {cart.reduce((sum, i) => sum + i.quantity, 0)} items
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Active Sort:</span>
                    <span className="text-gray-300 font-semibold">{sortOption}</span>
                  </div>
                  {checkoutInfo.firstName && (
                    <div className="flex justify-between border-t border-gray-800/60 pt-2 mt-2">
                      <span className="text-gray-500">Checkout Info:</span>
                      <span className="text-pink-400">
                        {checkoutInfo.firstName} {checkoutInfo.lastName} ({checkoutInfo.postalCode})
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Event Logs console log */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                    <Terminal className="h-3.5 w-3.5 text-purple-400" />
                    Trace Execution Logs
                  </h4>
                  <button
                    onClick={clearConsoleLogs}
                    className="text-[10px] text-red-400 hover:text-red-300 flex items-center gap-1 focus:outline-none"
                  >
                    <Trash2 className="h-3 w-3" />
                    Clear
                  </button>
                </div>

                <div className="bg-gray-950 rounded-lg border border-gray-800 p-3 h-36 overflow-y-auto font-mono text-[10px] space-y-1.5">
                  {consoleLogs.length === 0 ? (
                    <p className="text-gray-600 italic">No events logged. Start clicking around!</p>
                  ) : (
                    consoleLogs.map((log, i) => {
                      const isErr = log.includes('Error') || log.includes('failure') || log.includes('crash') || log.includes('blocked');
                      const isGlitch = log.includes('Glitch');
                      let txtColor = 'text-gray-400';
                      if (isErr) txtColor = 'text-red-400';
                      else if (isGlitch) txtColor = 'text-amber-400';
                      else if (log.includes('QA Panel')) txtColor = 'text-emerald-400';

                      return (
                        <div key={i} className={`leading-normal border-b border-gray-900/40 pb-1 ${txtColor}`}>
                          {log}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            </div>

            {/* Drawer Footer Actions */}
            <div className="p-4 border-t border-gray-800 bg-gray-950/80 flex items-center gap-3">
              <button
                onClick={() => {
                  resetState();
                  alert('QA State reset.');
                }}
                className="flex-1 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors border border-gray-800 cursor-pointer shadow-2xs"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Reset App State
              </button>

              <button
                onClick={() => {
                  changeUserTypeDirectly(null);
                  setIsOpen(false);
                }}
                className="flex-1 py-2.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 hover:text-red-300 font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors border border-red-500/20 cursor-pointer"
              >
                <X className="h-3.5 w-3.5" />
                Force Logoff
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
