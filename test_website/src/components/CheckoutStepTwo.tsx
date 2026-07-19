/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useApp } from '../context/AppContext';
import { ProductImage } from './ProductImage';
import { ArrowLeft, CheckCircle2, ShieldCheck, Landmark, Truck } from 'lucide-react';

export const CheckoutStepTwo: React.FC = () => {
  const {
    cart,
    setPageView,
    resetState,
    user,
  } = useApp();

  const isProblemUser = user === 'problem_user';
  const isVisualUser = user === 'visual_user';
  const isErrorUser = user === 'error_user';

  // Calculations
  const subtotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const tax = parseFloat((subtotal * 0.08).toFixed(2));
  const total = parseFloat((subtotal + tax).toFixed(2));

  const handleFinish = () => {
    // Simulate error user crash on payment dispatch
    if (isErrorUser) {
      console.error('[Error User Simulation] PaymentGatewayException: Transaction authentication timeout (code: 504).');
      alert('Epic sadface: Payment processor declined transactions. Checkout failed.');
      return;
    }

    // Go to next complete state
    setPageView('checkout-complete');
  };

  const handleCancel = () => {
    setPageView('inventory');
  };

  const containerClass = isVisualUser
    ? 'flex bg-pink-100 p-8 font-mono border-t-8 border-yellow-400 rotate-1'
    : 'max-w-4xl mx-auto py-8 px-6 font-sans';

  return (
    <div className={`min-h-screen bg-gray-50/50 ${containerClass}`} id="checkout_summary_container">
      <div className={isVisualUser ? '' : 'max-w-4xl mx-auto'}>
        {/* Step Header */}
        <div className="mb-6">
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
            <span>Step 2 of 2</span>
            <span>•</span>
            <span className="text-emerald-600">Invoice Overview</span>
          </div>
          <h2 className="text-xl md:text-2xl font-black text-gray-900 tracking-tight" data-test="title">
            Checkout: Overview
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Panel: Items review */}
          <div className="lg:col-span-7 space-y-4 cart_list">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 border-b border-gray-200 pb-1">
              Items Ordered
            </h3>

            {cart.map((item) => {
              const imageKeyToUse = isProblemUser ? 'dog-bug' : item.product.imageKey;

              return (
                <div
                  key={item.product.id}
                  className="bg-white rounded-xl shadow-xs border border-gray-200 p-4 flex gap-4 items-center"
                >
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-emerald-50 text-emerald-700 font-bold font-mono text-xs border border-emerald-100">
                    {item.quantity}
                  </div>
                  <div className="h-14 w-14 shrink-0 bg-gray-50 flex items-center justify-center p-1 rounded-md border border-gray-100">
                    <ProductImage imageKey={imageKeyToUse} className="w-auto h-full max-h-12 object-contain" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-gray-900 text-sm tracking-tight">{item.product.name}</h4>
                    <p className="text-[11px] text-gray-400 line-clamp-1 mt-0.5">{item.product.description}</p>
                  </div>
                  <span className="text-gray-900 font-extrabold font-mono text-sm shrink-0">
                    ${item.product.price.toFixed(2)}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Right Panel: Invoice Totals & Info */}
          <div className="lg:col-span-5 bg-white rounded-xl shadow-xs border border-gray-200 p-6 space-y-6">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider border-b border-gray-100 pb-3">
              Payment & Shipping Information
            </h3>

            {/* Simulated Info Blocks */}
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <span className="text-gray-400 font-bold uppercase tracking-wider block text-[10px]">Payment Info</span>
                <div className="flex items-center gap-1 text-gray-700 font-semibold">
                  <Landmark className="h-3.5 w-3.5 text-emerald-600" />
                  <span>SauceCard #31043</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-gray-400 font-bold uppercase tracking-wider block text-[10px]">Shipping Info</span>
                <div className="flex items-center gap-1 text-gray-700 font-semibold">
                  <Truck className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Pony Express Delivery!</span>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4 space-y-2.5">
              <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Price Breakdown</h4>

              {/* Subtotal */}
              <div className="flex justify-between text-xs text-gray-600">
                <span>Item total</span>
                <span className="summary_subtotal_label font-semibold font-mono">
                  ${subtotal.toFixed(2)}
                </span>
              </div>

              {/* Tax */}
              <div className="flex justify-between text-xs text-gray-600">
                <span>Tax (8%)</span>
                <span className="summary_tax_label font-semibold font-mono">
                  ${tax.toFixed(2)}
                </span>
              </div>

              {/* Grand Total */}
              <div className="flex justify-between pt-3 border-t border-gray-200 text-sm font-bold text-gray-900">
                <span>Total Due</span>
                <span className="summary_total_label font-extrabold font-mono text-emerald-600">
                  ${total.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Safety guarantee */}
            <div className="bg-gray-50 rounded-lg p-3 flex gap-2.5 text-[11px] text-gray-500 leading-normal border border-gray-200/50">
              <ShieldCheck className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
              <span>
                Your billing connection is fully secured. Clicking 'Finish' completes your purchase order.
              </span>
            </div>

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-gray-200">
              <button
                id="cancel"
                onClick={handleCancel}
                className="w-full sm:w-auto px-4 py-2.5 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors duration-150 cursor-pointer shadow-2xs"
              >
                <ArrowLeft className="h-4 w-4" />
                Cancel
              </button>

              <button
                id="finish"
                data-test="finish"
                onClick={handleFinish}
                className="w-full sm:w-auto px-5 py-2.5 bg-gray-900 hover:bg-emerald-600 text-white font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
              >
                <CheckCircle2 className="h-4 w-4" />
                Finish
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
