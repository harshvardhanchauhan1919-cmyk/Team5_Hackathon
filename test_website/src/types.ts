/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type UserType =
  | 'standard_user'
  | 'locked_out_user'
  | 'problem_user'
  | 'performance_glitch_user'
  | 'visual_user'
  | 'error_user';

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  imageKey: string;
  buggyImageKey?: string; // used for problem_user
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface CheckoutInfo {
  firstName: string;
  lastName: string;
  postalCode: string;
}

export type PageView =
  | 'login'
  | 'inventory'
  | 'details'
  | 'cart'
  | 'checkout-1'
  | 'checkout-2'
  | 'checkout-complete';

export type SortOption = 'az' | 'za' | 'lohi' | 'hilo';

export interface AppState {
  user: UserType | null;
  currentPage: PageView;
  selectedProductId: number | null;
  cart: CartItem[];
  sortOption: SortOption;
  checkoutInfo: CheckoutInfo;
  consoleLogs: string[];
}
