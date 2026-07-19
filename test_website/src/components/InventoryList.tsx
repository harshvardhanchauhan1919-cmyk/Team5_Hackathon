/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useApp } from '../context/AppContext';
import { PRODUCTS } from '../data';
import { ProductImage } from './ProductImage';
import { Star, ShieldAlert } from 'lucide-react';
import { SortOption } from '../types';

export const InventoryList: React.FC = () => {
  const {
    user,
    cart,
    sortOption,
    setSortOption,
    addToCart,
    removeFromCart,
    selectProduct,
  } = useApp();

  const isProblemUser = user === 'problem_user';
  const isVisualUser = user === 'visual_user';

  // Get active cart item IDs
  const cartItemIds = cart.map((item) => item.product.id);

  // Sorting logic
  const sortedProducts = [...PRODUCTS].sort((a, b) => {
    switch (sortOption) {
      case 'az':
        return a.name.localeCompare(b.name);
      case 'za':
        return b.name.localeCompare(a.name);
      case 'lohi':
        return a.price - b.price;
      case 'hilo':
        return b.price - a.price;
      default:
        return 0;
    }
  });

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    // Problem user fails to update sorting, or changes it to Z-A regardless of what was clicked
    if (isProblemUser) {
      setSortOption('za'); // Problem user is stuck sorting in custom ways or fails to sort
    } else {
      setSortOption(e.target.value as SortOption);
    }
  };

  // Helper to resolve test-compliant IDs for buttons
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

  // Visual user layouts are skewed
  const containerClass = isVisualUser
    ? 'max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 md:grid-cols-4 gap-8' // Unbalanced columns
    : 'max-w-7xl mx-auto px-6 py-8';

  const subHeaderClass = isVisualUser
    ? 'flex flex-col gap-4 items-start bg-red-100 p-6 rounded border border-red-300'
    : 'flex items-center justify-between border-b border-gray-200 pb-4 mb-6';

  const gridClass = isVisualUser
    ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-4' // Awkward spacing
    : 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-10';

  const itemCardClass = isVisualUser
    ? 'bg-white rounded-none shadow-sm hover:shadow-md border-t-8 border-l-4 border-pink-500 overflow-hidden transform rotate-1 transition-all'
    : 'bg-white rounded-xl shadow-xs border border-gray-200/80 overflow-hidden hover:shadow-sm hover:border-gray-300 transition-all duration-200 flex flex-col justify-between';

  return (
    <div className={`font-sans min-h-screen bg-gray-50/50 ${containerClass}`}>
      {/* Sub Header Container */}
      <div className={subHeaderClass}>
        <h2 className="text-xl md:text-2xl font-black text-gray-900 tracking-tight" data-test="title">
          Products{isVisualUser ? ' (Layout Distorted)' : ''}
        </h2>

        {/* Sort select dropdown */}
        <div className="flex items-center gap-2 select_container">
          <label htmlFor="sort-dropdown" className="text-xs font-bold text-gray-500 font-mono tracking-wider">
            SORT BY:
          </label>
          <select
            id="sort-dropdown"
            className="product_sort_container bg-white border border-gray-300 text-gray-700 text-xs font-semibold rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-gray-400 cursor-pointer shadow-2xs"
            data-test="product-sort-container"
            value={sortOption}
            onChange={handleSortChange}
          >
            <option value="az">Name (A to Z)</option>
            <option value="za">Name (Z to A)</option>
            <option value="lohi">Price (low to high)</option>
            <option value="hilo">Price (high to low)</option>
          </select>
        </div>
      </div>

      {/* Problem User Alert banner */}
      {isProblemUser && (
        <div className="mb-6 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl p-4 flex items-start gap-3 text-xs leading-relaxed max-w-7xl mx-auto shadow-2xs">
          <ShieldAlert className="h-5 w-5 text-amber-500 shrink-0 mt-0.5 animate-bounce" />
          <div>
            <p className="font-bold">Problem User Session Enabled:</p>
            <p className="mt-1">
              All inventory graphics are swapped with the 404-dog image. Product sorting has been locked. Product
              detailing redirect mappings are corrupted. Standard cart increments of certain items (ID 0, ID 1) are disabled,
              and Onesies (ID 2) add Backpacks (ID 4) instead.
            </p>
          </div>
        </div>
      )}

      {/* Grid List */}
      <div className={`${gridClass} inventory_list`} id="inventory_container">
        {sortedProducts.map((product) => {
          const inCart = cartItemIds.includes(product.id);
          const imageKeyToUse = isProblemUser ? 'dog-bug' : product.imageKey;

          return (
            <div
              key={product.id}
              className={`${itemCardClass} inventory_item p-5`}
              id={`item_${product.id}_title_link`}
            >
              {/* Image click details */}
              <div
                className="inventory_item_img h-48 md:h-52 w-full mb-4 cursor-pointer relative group overflow-hidden rounded-lg bg-gray-50 flex items-center justify-center p-4 border border-gray-100"
                onClick={() => selectProduct(product.id)}
              >
                <ProductImage
                  imageKey={imageKeyToUse}
                  className="w-auto h-full max-h-40 object-contain group-hover:scale-102 transition-transform duration-200"
                  skewed={isVisualUser}
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/2 rounded-lg transition-colors duration-150" />
              </div>

              {/* Title & description container */}
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  {/* Rating indicator stars - Swag Labs details */}
                  <div className={`flex items-center gap-0.5 mb-2 ${isVisualUser ? 'hidden' : ''}`}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`h-3.5 w-3.5 ${
                          star <= 4 ? 'fill-amber-400 text-amber-400' : 'text-gray-200 fill-gray-200'
                        }`}
                      />
                    ))}
                    <span className="text-[10px] text-gray-400 font-semibold ml-1.5">(4.0)</span>
                  </div>

                  {/* Click name details */}
                  <h3
                    id={`item_${product.id}_title_link`}
                    className={`inventory_item_name font-bold text-gray-900 hover:text-emerald-600 cursor-pointer transition-colors duration-150 ${
                      isVisualUser ? 'text-sm mt-3 leading-tight text-pink-600 line-through' : 'text-base md:text-lg mb-1 tracking-tight'
                    }`}
                    onClick={() => selectProduct(product.id)}
                  >
                    {product.name}
                  </h3>

                  <p
                    className={`inventory_item_desc text-gray-500 text-xs leading-relaxed ${
                      isVisualUser ? 'text-[9px] truncate max-w-[200px]' : 'line-clamp-3 mb-4'
                    }`}
                  >
                    {product.description}
                  </p>
                </div>

                {/* Price and Cart Buttons */}
                <div className="pricebar flex items-center justify-between pt-4 border-t border-gray-100 mt-auto">
                  <span
                    className={`inventory_item_price text-gray-900 font-extrabold font-mono ${
                      isVisualUser ? 'text-3xl text-sky-500 font-serif' : 'text-lg md:text-xl'
                    }`}
                  >
                    ${product.price.toFixed(2)}
                  </span>

                  {inCart ? (
                    <button
                      id={getButtonId(product.id, 'remove')}
                      data-test={getButtonId(product.id, 'remove')}
                      onClick={() => removeFromCart(product.id)}
                      className="btn_secondary btn_inventory px-4 py-2 text-xs font-bold rounded-lg bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 transition-all duration-150 cursor-pointer"
                    >
                      Remove
                    </button>
                  ) : (
                    <button
                      id={getButtonId(product.id, 'add')}
                      data-test={getButtonId(product.id, 'add')}
                      onClick={() => addToCart(product.id)}
                      className="btn_primary btn_inventory px-4 py-2 text-xs font-bold rounded-lg bg-gray-900 text-white hover:bg-emerald-600 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
                    >
                      Add to Cart
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
