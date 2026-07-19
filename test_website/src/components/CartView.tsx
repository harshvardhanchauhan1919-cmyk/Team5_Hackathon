/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useApp } from '../context/AppContext';
import { ProductImage } from './ProductImage';
import { ArrowLeft, CreditCard, ShoppingBag, Trash2 } from 'lucide-react';

export const CartView: React.FC = () => {
  const {
    cart,
    removeFromCart,
    setPageView,
    selectProduct,
    user,
  } = useApp();

  const isProblemUser = user === 'problem_user';
  const isVisualUser = user === 'visual_user';

  const handleContinueShopping = () => {
    selectProduct(null);
    setPageView('inventory');
  };

  const handleCheckout = () => {
    setPageView('checkout-1');
  };

  const getButtonId = (id: number) => {
    switch (id) {
      case 4:
        return 'remove-sauce-labs-backpack';
      case 0:
        return 'remove-sauce-labs-bike-light';
      case 1:
        return 'remove-sauce-labs-bolt-t-shirt';
      case 5:
        return 'remove-sauce-labs-fleece-jacket';
      case 2:
        return 'remove-sauce-labs-onesie';
      case 3:
        return 'remove-test.allthethings()-t-shirt-(red)';
      default:
        return 'remove-unknown';
    }
  };

  const cartClass = isVisualUser
    ? 'flex flex-col-reverse bg-yellow-100 p-4 font-mono'
    : 'max-w-4xl mx-auto py-8 px-6 font-sans';

  return (
    <div className={`min-h-screen bg-gray-50/50 ${cartClass}`} id="cart_contents_container">
      <div className={isVisualUser ? '' : 'max-w-4xl mx-auto'}>
        {/* Title */}
        <h2 className={`text-xl md:text-2xl font-black text-gray-900 mb-6 tracking-tight ${isVisualUser ? 'text-4xl text-purple-700' : ''}`} data-test="title">
          Your Cart
        </h2>

        {cart.length === 0 ? (
          <div className="bg-white rounded-xl shadow-xs border border-gray-200 p-8 md:p-12 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-50 text-gray-400 mb-4">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <h3 className="text-sm font-bold text-gray-800">Your cart is empty</h3>
            <p className="text-xs text-gray-400 mt-1 mb-6">Looks like you haven't added any products to your cart yet.</p>
            <button
              id="continue-shopping"
              data-test="continue-shopping"
              onClick={handleContinueShopping}
              className="px-4 py-2 bg-gray-900 hover:bg-emerald-600 text-white font-bold rounded-lg text-xs transition-colors duration-150 cursor-pointer shadow-xs"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="space-y-6 cart_list">
            {/* Table headers */}
            <div className="hidden sm:grid grid-cols-12 gap-4 px-4 py-2 border-b border-gray-200 text-xs font-bold text-gray-400 uppercase tracking-wider">
              <div className="col-span-1 text-center">QTY</div>
              <div className="col-span-11">Item Description</div>
            </div>

            {/* Cart Items list */}
            {cart.map((item) => {
              const imageKeyToUse = isProblemUser ? 'dog-bug' : item.product.imageKey;

              return (
                <div
                  key={item.product.id}
                  className="inventory_item bg-white rounded-xl shadow-xs border border-gray-200/80 overflow-hidden p-4 sm:p-6 grid grid-cols-1 sm:grid-cols-12 gap-4 items-center"
                >
                  {/* Quantity indicator */}
                  <div className="col-span-1 flex items-center justify-center sm:border-r sm:border-gray-200 sm:pr-4">
                    <span
                      data-test="item-quantity"
                      className="cart_quantity flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 font-bold font-mono text-sm border border-emerald-100"
                    >
                      {item.quantity}
                    </span>
                  </div>

                  {/* Product Details info */}
                  <div className="col-span-11 flex flex-col sm:flex-row items-center gap-4 sm:pl-4">
                    {/* Item Image */}
                    <div
                      className="h-20 w-20 shrink-0 cursor-pointer bg-gray-50 flex items-center justify-center p-2 rounded-lg border border-gray-100"
                      onClick={() => selectProduct(item.product.id)}
                    >
                      <ProductImage imageKey={imageKeyToUse} className="w-auto h-full max-h-16 object-contain" />
                    </div>

                    {/* Meta details */}
                    <div className="flex-1 text-center sm:text-left">
                      <h3
                        onClick={() => selectProduct(item.product.id)}
                        className="inventory_item_name font-bold text-gray-900 hover:text-emerald-600 text-base md:text-lg mb-1 cursor-pointer transition-colors duration-150 tracking-tight"
                      >
                        {item.product.name}
                      </h3>
                      <p className="inventory_item_desc text-gray-400 text-xs line-clamp-2 leading-relaxed">
                        {item.product.description}
                      </p>
                    </div>

                    {/* Price and delete button */}
                    <div className="flex sm:flex-col items-center sm:items-end gap-3 justify-between w-full sm:w-auto shrink-0 border-t sm:border-t-0 border-gray-200 pt-3 sm:pt-0">
                      <span className="inventory_item_price text-gray-900 font-extrabold font-mono text-base md:text-lg">
                        ${item.product.price.toFixed(2)}
                      </span>

                      <button
                        id={getButtonId(item.product.id)}
                        data-test={getButtonId(item.product.id)}
                        onClick={() => removeFromCart(item.product.id)}
                        className="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors focus:outline-none cursor-pointer"
                        title="Remove Item"
                      >
                        <Trash2 className="h-4.5 w-4.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Footer Navigation bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-gray-200">
              <button
                id="continue-shopping"
                data-test="continue-shopping"
                onClick={handleContinueShopping}
                className="w-full sm:w-auto px-5 py-3 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 font-bold rounded-lg text-xs flex items-center justify-center gap-2 transition-colors duration-150 cursor-pointer shadow-2xs"
              >
                <ArrowLeft className="h-4 w-4" />
                Continue Shopping
              </button>

              <button
                id="checkout"
                data-test="checkout"
                onClick={handleCheckout}
                className="w-full sm:w-auto px-6 py-3 bg-gray-900 hover:bg-emerald-600 text-white font-bold rounded-lg text-xs flex items-center justify-center gap-2 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
              >
                <CreditCard className="h-4 w-4" />
                Checkout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
