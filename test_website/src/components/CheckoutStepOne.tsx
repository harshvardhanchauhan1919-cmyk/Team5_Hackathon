/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { CheckoutInfo } from '../types';
import { ArrowLeft, User, MapPin, ShieldAlert, BadgeInfo } from 'lucide-react';

export const CheckoutStepOne: React.FC = () => {
  const {
    checkoutInfo,
    setCheckoutInfo,
    setPageView,
    user,
  } = useApp();

  const isProblemUser = user === 'problem_user';
  const isVisualUser = user === 'visual_user';
  const isErrorUser = user === 'error_user';

  // Local state initialized with current context info
  const [firstName, setFirstName] = useState(checkoutInfo.firstName);
  const [lastName, setLastName] = useState(isProblemUser ? 'Problem' : checkoutInfo.lastName);
  const [postalCode, setPostalCode] = useState(checkoutInfo.postalCode);
  const [error, setError] = useState<string | null>(null);

  const handleLastNameChange = (val: string) => {
    // Problem user forces the Last Name input to remain 'Problem' or blocks typing
    if (isProblemUser) {
      setLastName('Problem');
    } else {
      setLastName(val);
    }
  };

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Form Validation rules matching Sauce Demo
    if (!firstName.trim()) {
      setError('Error: First Name is required');
      return;
    }
    if (!lastName.trim()) {
      setError('Error: Last Name is required');
      return;
    }
    if (!postalCode.trim()) {
      setError('Error: Postal Code is required');
      return;
    }

    // Simulate error user failures on clicking continue
    if (isErrorUser) {
      console.error('[Error User Simulation] RuntimeException: NullPointer in form submission controller.');
      setError('Epic sadface: An unexpected technical failure occurred on submission sequence.');
      alert('Epic sadface: Form submission handler is corrupt.');
      return;
    }

    // Save state and proceed
    setCheckoutInfo({
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      postalCode: postalCode.trim(),
    });

    setPageView('checkout-2');
  };

  const handleCancel = () => {
    setPageView('cart');
  };

  const containerClass = isVisualUser
    ? 'flex bg-sky-100 p-2 border-l-8 border-pink-600 font-serif'
    : 'max-w-xl mx-auto py-8 px-6 font-sans';

  const inputClass = "w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 focus:bg-white transition-all duration-150 shadow-2xs";

  return (
    <div className={`min-h-screen bg-gray-50/50 ${containerClass}`} id="checkout_info_container">
      <div className={isVisualUser ? '' : 'w-full max-w-lg mx-auto bg-white p-6 md:p-8 shadow-xs border border-gray-200 rounded-xl'}>
        {/* Step Header */}
        <div className="mb-6">
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
            <span>Step 1 of 2</span>
            <span>•</span>
            <span className="text-emerald-600">Billing Information</span>
          </div>
          <h2 className="text-xl md:text-2xl font-black text-gray-900 tracking-tight" data-test="title">
            Checkout: Your Information
          </h2>
        </div>

        {/* Problem user details notice */}
        {isProblemUser && (
          <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl p-3 flex gap-2 text-xs">
            <BadgeInfo className="h-4.5 w-4.5 text-amber-500 shrink-0 mt-0.5" />
            <p>
              <strong>Problem User Glitch Active:</strong> Last name input has been hijacked and locked to "Problem".
            </p>
          </div>
        )}

        <form onSubmit={handleContinue} className="space-y-4">
          {/* First Name */}
          <div className="space-y-1">
            <label htmlFor="first-name" className="text-xs font-bold text-gray-500 block uppercase tracking-wider">
              First Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-4 w-4 text-gray-400" />
              </div>
              <input
                id="first-name"
                data-test="firstName"
                type="text"
                placeholder="First Name"
                className={inputClass}
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
          </div>

          {/* Last Name */}
          <div className="space-y-1">
            <label htmlFor="last-name" className="text-xs font-bold text-gray-500 block uppercase tracking-wider">
              Last Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-4 w-4 text-gray-400" />
              </div>
              <input
                id="last-name"
                data-test="lastName"
                type="text"
                placeholder="Last Name"
                className={`${inputClass} ${isProblemUser ? 'bg-amber-50 border-amber-200 cursor-not-allowed font-semibold text-amber-700' : ''}`}
                value={lastName}
                onChange={(e) => handleLastNameChange(e.target.value)}
              />
            </div>
          </div>

          {/* Postal Code */}
          <div className="space-y-1">
            <label htmlFor="postal-code" className="text-xs font-bold text-gray-500 block uppercase tracking-wider">
              Zip/Postal Code
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MapPin className="h-4 w-4 text-gray-400" />
              </div>
              <input
                id="postal-code"
                data-test="postalCode"
                type="text"
                placeholder="Zip/Postal Code"
                className={inputClass}
                value={postalCode}
                onChange={(e) => setPostalCode(e.target.value)}
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

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-6 border-t border-gray-200">
            <button
              id="cancel"
              type="button"
              onClick={handleCancel}
              className="w-full sm:w-auto px-5 py-2.5 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors duration-150 cursor-pointer shadow-2xs"
            >
              <ArrowLeft className="h-4 w-4" />
              Cancel
            </button>

            <button
              id="continue"
              type="submit"
              className="w-full sm:w-auto px-6 py-2.5 bg-gray-900 hover:bg-emerald-600 text-white font-bold rounded-lg text-xs shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
            >
              Continue
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
