/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { AppState, UserType, PageView, SortOption, CartItem, CheckoutInfo } from '../types';
import { PRODUCTS } from '../data';

interface AppContextType extends AppState {
  isNavigating: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  addToCart: (productId: number) => void;
  removeFromCart: (productId: number) => void;
  setSortOption: (option: SortOption) => void;
  setCheckoutInfo: (info: CheckoutInfo) => void;
  resetState: () => void;
  setPageView: (page: PageView) => void;
  selectProduct: (productId: number | null) => void;
  changeUserTypeDirectly: (userType: UserType | null) => void;
  clearConsoleLogs: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserType | null>(null);
  const [currentPage, setCurrentPageState] = useState<PageView>('login');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [sortOption, setSortOption] = useState<SortOption>('az');
  const [checkoutInfo, setCheckoutInfoState] = useState<CheckoutInfo>({
    firstName: '',
    lastName: '',
    postalCode: '',
  });
  const [consoleLogs, setConsoleLogs] = useState<string[]>([]);
  const [isNavigating, setIsNavigating] = useState(false);

  // Write a helper to log console events
  const addLog = (message: string, isError = false) => {
    const timestamp = new Date().toLocaleTimeString();
    const formatted = `[${timestamp}] ${message}`;
    setConsoleLogs((prev) => [formatted, ...prev]);
    if (isError) {
      console.error(message);
    } else {
      console.log(message);
    }
  };

  // Clear logs helper
  const clearConsoleLogs = () => {
    setConsoleLogs([]);
  };

  // Sync state to standard window elements for testing frameworks
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).sauceUser = user;
      (window as any).sauceCart = cart;
      (window as any).saucePage = currentPage;
    }
  }, [user, cart, currentPage]);

  // Handle page transitions, including performance glitch delay
  const setPageView = (page: PageView) => {
    if (user === 'performance_glitch_user') {
      setIsNavigating(true);
      addLog(`[Performance Glitch] Delaying navigation to "${page}" by 2.5 seconds...`);
      setTimeout(() => {
        setCurrentPageState(page);
        setIsNavigating(false);
        addLog(`Navigated to page: ${page}`);
      }, 2500);
    } else {
      setCurrentPageState(page);
      addLog(`Navigated to page: ${page}`);
    }
  };

  // Login handler
  const login = async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
    addLog(`Attempting login for user: "${username}"`);

    // Authentication rule
    if (password !== 'secret_sauce') {
      const errMsg = 'Epic sadface: Username and password do not match any user in this service';
      addLog(`Login failed: Invalid password`, true);
      return { success: false, error: errMsg };
    }

    const validUsernames: UserType[] = [
      'standard_user',
      'locked_out_user',
      'problem_user',
      'performance_glitch_user',
      'visual_user',
      'error_user',
    ];

    if (!validUsernames.includes(username as UserType)) {
      const errMsg = 'Epic sadface: Username and password do not match any user in this service';
      addLog(`Login failed: Username "${username}" not found`, true);
      return { success: false, error: errMsg };
    }

    if (username === 'locked_out_user') {
      const errMsg = 'Epic sadface: Sorry, this user has been locked out.';
      addLog(`Login blocked: User "${username}" is locked out`, true);
      return { success: false, error: errMsg };
    }

    // Handle performance glitch delay for login page action
    if (username === 'performance_glitch_user') {
      setIsNavigating(true);
      addLog(`[Performance Glitch] Simulating 2.5s login API delay...`);
      await new Promise((resolve) => setTimeout(resolve, 2500));
      setIsNavigating(false);
    }

    setUser(username as UserType);
    addLog(`User "${username}" logged in successfully`);
    setPageView('inventory');
    return { success: true };
  };

  // Logout handler
  const logout = () => {
    addLog(`User "${user}" logging out`);
    setUser(null);
    setCurrentPageState('login');
    setSelectedProductId(null);
    setCart([]);
    setSortOption('az');
    setCheckoutInfoState({ firstName: '', lastName: '', postalCode: '' });
  };

  // Product detailed page selection
  const selectProduct = (productId: number | null) => {
    // Problem user redirects clicked product to ID 5 (Fleece Jacket) in details view
    if (user === 'problem_user' && productId !== null && productId !== 5) {
      addLog(`[Problem User] Redirecting product click details of ID ${productId} to ID 5`);
      setSelectedProductId(5);
    } else {
      setSelectedProductId(productId);
    }
    setPageView(productId === null ? 'inventory' : 'details');
  };

  // Add to Cart
  const addToCart = (productId: number) => {
    const product = PRODUCTS.find((p) => p.id === productId);
    if (!product) return;

    // Simulate error user crash when adding certain items
    if (user === 'error_user' && (productId === 2 || productId === 3)) {
      const errMsg = `[Error User Simulation] Critical Exception: Failed to append product ID ${productId} to shopping cart sequence.`;
      addLog(errMsg, true);
      alert('Epic sadface: An unexpected client-side error occurred while writing to cart.');
      return;
    }

    // Simulate problem user bug:
    // Adding Onesie (id: 2) actually adds the Backpack (id: 4) instead, and trying to add Bike Light (id: 0) does nothing!
    if (user === 'problem_user') {
      if (productId === 2) {
        addLog(`[Problem User] Attempted to add Onesie (ID: 2). Swapping with Backpack (ID: 4)`);
        const backpackProduct = PRODUCTS.find((p) => p.id === 4)!;
        setCart((prev) => {
          if (prev.some((item) => item.product.id === 4)) return prev;
          return [...prev, { product: backpackProduct, quantity: 1 }];
        });
        return;
      } else if (productId === 0 || productId === 1) {
        addLog(`[Problem User] Blocked adding product ID ${productId} to cart`);
        return;
      }
    }

    setCart((prev) => {
      // Swag Labs only allows quantity 1 per item
      if (prev.some((item) => item.product.id === productId)) return prev;
      addLog(`Added to cart: ${product.name}`);
      return [...prev, { product, quantity: 1 }];
    });
  };

  // Remove from Cart
  const removeFromCart = (productId: number) => {
    // Simulate error user crash on removing certain items
    if (user === 'error_user' && (productId === 2 || productId === 3)) {
      const errMsg = `[Error User Simulation] Critical Exception: IndexOutOfRange in state array deletion for item ID ${productId}.`;
      addLog(errMsg, true);
      alert('Epic sadface: Client-side exception. State manipulation failed.');
      return;
    }

    // Simulate problem user bug: removing certain items fails
    if (user === 'problem_user' && (productId === 4 || productId === 5)) {
      addLog(`[Problem User] Blocked removing product ID ${productId} from cart`);
      return;
    }

    setCart((prev) => {
      addLog(`Removed from cart product ID: ${productId}`);
      return prev.filter((item) => item.product.id !== productId);
    });
  };

  // Checkout info entry
  const setCheckoutInfo = (info: CheckoutInfo) => {
    // Problem user overrides the last name or prevents changing it
    if (user === 'problem_user') {
      addLog(`[Problem User] Corrupting checkout info: locking last name`);
      setCheckoutInfoState({
        firstName: info.firstName,
        lastName: 'Problem', // Locks the last name
        postalCode: info.postalCode,
      });
    } else {
      setCheckoutInfoState(info);
    }
  };

  // Reset Application State
  const resetState = () => {
    addLog(`Resetting application state...`);
    setCart([]);
    setSortOption('az');
    setSelectedProductId(null);
    setCheckoutInfoState({ firstName: '', lastName: '', postalCode: '' });
  };

  // Direct QA switcher
  const changeUserTypeDirectly = (userType: UserType | null) => {
    addLog(`[QA Panel] Direct user profile change: ${userType}`);
    setUser(userType);
    if (!userType) {
      setCurrentPageState('login');
    } else {
      setCurrentPageState('inventory');
    }
  };

  return (
    <AppContext.Provider
      value={{
        user,
        currentPage,
        selectedProductId,
        cart,
        sortOption,
        checkoutInfo,
        consoleLogs,
        isNavigating,
        login,
        logout,
        addToCart,
        removeFromCart,
        setSortOption,
        setCheckoutInfo,
        resetState,
        setPageView,
        selectProduct,
        changeUserTypeDirectly,
        clearConsoleLogs,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
