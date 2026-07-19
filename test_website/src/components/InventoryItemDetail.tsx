/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useApp } from '../context/AppContext';
import { PRODUCTS } from '../data';
import { ProductImage } from './ProductImage';
import { ArrowLeft, Star, Shield, ArrowUpRight } from 'lucide-react';

export const InventoryItemDetail: React.FC = () => {
  const {
    user,
    selectedProductId,
    cart,
    addToCart,
    removeFromCart,
    selectProduct,
  } = useApp();

  const isProblemUser = user === 'problem_user';
  const isVisualUser = user === 'visual_user';

  // Find product details
  const product = PRODUCTS.find((p) => p.id === selectedProductId);

  if (!product) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-12 text-center font-sans">
        <p className="text-lg font-semibold text-red-500">Error: Product details could not be found.</p>
        <button
          onClick={() => selectProduct(null)}
          className="mt-4 px-4 py-2 bg-slate-800 text-white rounded-xl text-xs hover:bg-emerald-500 transition-colors"
        >
          Back to products
        </button>
      </div>
    );
  }

  const inCart = cart.some((item) => item.product.id === product.id);
  const imageKeyToUse = isProblemUser ? 'dog-bug' : product.imageKey;

  const getButtonId = (id: number, action: 'add' | 'remove') => {
    const actionPrefix = action === 'add' ? 'add-to-cart' : 'remove';
    switch (id) {
      case 4:
        return `${actionPrefix}-sauce-labs-backpack`;
      case 0:
        return `${actionPrefix}-sauce-labs-bike-light`;
      case 1:
        return `${actionPrefix}-sauce-labs-bolt-t-shirt`;
      case 5:
        return `${actionPrefix}-sauce-labs-fleece-jacket`;
      case 2:
        return `${actionPrefix}-sauce-labs-onesie`;
      case 3:
        return `${actionPrefix}-test.allthethings()-t-shirt-(red)`;
      default:
        return `${actionPrefix}-unknown`;
    }
  };

  const backButtonClass = isVisualUser
    ? 'text-pink-500 text-xs flex items-center gap-1 border-4 border-yellow-500 rotate-12 mb-8 ml-20'
    : 'flex items-center gap-2 text-gray-500 hover:text-emerald-600 text-xs font-bold uppercase tracking-wider mb-8 transition-colors duration-150 cursor-pointer';

  return (
    <div className="font-sans min-h-screen bg-gray-50/50 py-8 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Back navigation button */}
        <button
          id="back-to-products"
          data-test="back-to-products"
          onClick={() => selectProduct(null)}
          className={backButtonClass}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to products
        </button>

        {/* Detailed item card */}
        <div
          className={`bg-white rounded-xl shadow-xs border border-gray-200 overflow-hidden p-6 md:p-10 ${
            isVisualUser ? 'transform -skew-y-3 border-r-8 border-b-8 border-pink-400' : ''
          }`}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-center">
            {/* Left: Product Image */}
            <div className="h-64 sm:h-80 md:h-96 w-full relative bg-gray-50 flex items-center justify-center p-6 rounded-lg border border-gray-100">
              <ProductImage imageKey={imageKeyToUse} className="w-auto h-full max-h-80 object-contain" skewed={isVisualUser} />
              {isProblemUser && (
                <div className="absolute top-2 left-2 bg-amber-500 text-white text-[9px] font-mono font-bold px-2 py-1 rounded">
                  BUG Mapped (sl-404)
                </div>
              )}
            </div>

            {/* Right: Product Meta & Description */}
            <div className="flex flex-col justify-center">
              {/* Product Badges */}
              <div className="flex items-center gap-2 mb-4">
                <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-md">
                  Active Stock
                </span>
                <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-gray-50 text-gray-600 border border-gray-200 rounded-md">
                  ID: {product.id}
                </span>
              </div>

              {/* Product Title */}
              <h1
                id="inventory-item-name"
                className={`text-2xl md:text-3.5xl font-black text-gray-900 tracking-tight leading-tight mb-3 ${
                  isVisualUser ? 'text-sm text-yellow-600' : ''
                }`}
              >
                {product.name}
              </h1>

              {/* Star details */}
              <div className="flex items-center gap-1 mb-5">
                <div className="flex items-center gap-0.5">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`h-4 w-4 ${
                        star <= 4 ? 'fill-amber-400 text-amber-400' : 'text-gray-200 fill-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-gray-400 font-semibold ml-2">(4.0 out of 5 based on 184 reviews)</span>
              </div>

              {/* Product Description */}
              <p
                id="inventory-item-desc"
                className="text-gray-600 text-sm md:text-base leading-relaxed mb-6"
              >
                {product.description}
              </p>

              {/* Technical disclaimer */}
              <div className="bg-gray-50 border border-gray-200/60 rounded-lg p-4 flex gap-3 mb-8">
                <Shield className="h-5 w-5 text-gray-400 shrink-0 mt-0.5" />
                <div className="text-xs text-gray-500 leading-relaxed">
                  <p className="font-semibold text-gray-700">Sauce Verification Guarantee</p>
                  <p className="mt-0.5">
                    This item includes our standard lab security certificate and full-chain automated test trace records.
                  </p>
                </div>
              </div>

              {/* Pricing & Cart controls */}
              <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                <div className="flex flex-col">
                  <span className="text-xs text-gray-400 font-bold uppercase tracking-wider">Unit Price</span>
                  <span
                    id="inventory-item-price"
                    className="text-2xl md:text-3.5xl font-extrabold font-mono text-gray-900 mt-0.5"
                  >
                    ${product.price.toFixed(2)}
                  </span>
                </div>

                {inCart ? (
                  <button
                    id={getButtonId(product.id, 'remove')}
                    data-test={getButtonId(product.id, 'remove')}
                    onClick={() => removeFromCart(product.id)}
                    className="px-6 py-3.5 text-xs font-bold rounded-lg bg-gray-100 text-gray-700 border border-gray-200 hover:bg-red-50 hover:text-red-600 hover:border-red-100 shadow-sm transition-all duration-150 cursor-pointer"
                  >
                    Remove from Cart
                  </button>
                ) : (
                  <button
                    id={getButtonId(product.id, 'add')}
                    data-test={getButtonId(product.id, 'add')}
                    onClick={() => addToCart(product.id)}
                    className="px-6 py-3.5 text-xs font-bold rounded-lg bg-gray-900 text-white hover:bg-emerald-600 hover:shadow-md transition-all duration-150 cursor-pointer flex items-center gap-2"
                  >
                    Add to Cart
                    <ArrowUpRight className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
