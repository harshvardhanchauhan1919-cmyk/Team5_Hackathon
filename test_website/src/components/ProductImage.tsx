/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';

interface ProductImageProps {
  imageKey: string;
  className?: string;
  skewed?: boolean; // visual_user effect
}

export const ProductImage: React.FC<ProductImageProps> = ({
  imageKey,
  className = 'w-full h-full',
  skewed = false,
}) => {
  const transformClass = skewed ? 'skew-y-12 scale-75 origin-center border-red-500 border-4' : '';

  // Render SVGs representing each product
  switch (imageKey) {
    case 'backpack':
      return (
        <svg
          id="svg-backpack"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Main Body */}
          <rect x="25" y="35" width="50" height="50" rx="12" fill="#4B5563" />
          {/* Front Pocket */}
          <rect x="32" y="55" width="36" height="24" rx="6" fill="#374151" />
          <path d="M32 61H68" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" />
          {/* Top Handle */}
          <path d="M40 35V28C40 25.7909 41.7909 24 44 24H56C58.2091 24 60 25.7909 60 28V35" stroke="#1F2937" strokeWidth="4" />
          {/* Logo Badge */}
          <circle cx="50" cy="45" r="5" fill="#EF4444" />
          <path d="M48 45L52 45" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          {/* Straps */}
          <path d="M28 35V50" stroke="#111827" strokeWidth="3" strokeLinecap="round" />
          <path d="M72 35V50" stroke="#111827" strokeWidth="3" strokeLinecap="round" />
          {/* Zipper pulls */}
          <circle cx="50" cy="58" r="1.5" fill="#F59E0B" />
        </svg>
      );

    case 'bike-light':
      return (
        <svg
          id="svg-bike-light"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Mount Bracket */}
          <rect x="42" y="55" width="16" height="20" rx="4" fill="#374151" />
          <circle cx="50" cy="70" r="4" fill="#111827" />
          {/* Light Body */}
          <rect x="30" y="30" width="40" height="26" rx="8" transform="rotate(-10 50 43)" fill="#1F2937" />
          {/* Lens Cap */}
          <rect x="64" y="30" width="8" height="20" rx="3" fill="#9CA3AF" />
          {/* Light Source (Red Glow) */}
          <circle cx="70" cy="40" r="6" fill="#EF4444" />
          <circle cx="70" cy="40" r="3" fill="#FEE2E2" />
          {/* Reflector details */}
          <path d="M36 34L44 32" stroke="#4B5563" strokeWidth="2" strokeLinecap="round" />
          <path d="M38 42L46 40" stroke="#4B5563" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );

    case 'bolt-tshirt':
      return (
        <svg
          id="svg-bolt-tshirt"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Folded Shirt Outline */}
          <path d="M25 25C25 22 35 20 50 20C65 20 75 22 75 25L82 42C82 44 78 46 75 44L72 38V76C72 79 68 82 64 82H36C32 82 28 79 28 76V38L25 44C22 46 18 44 18 42L25 25Z" fill="#1E293B" />
          {/* Collar Line */}
          <path d="M42 20C42 24 58 24 58 20" stroke="#475569" strokeWidth="3" strokeLinecap="round" />
          {/* Lightning Bolt Graphic */}
          <path d="M52 28L40 48H50L46 70L62 45H50L52 28Z" fill="#FBBF24" stroke="#F59E0B" strokeWidth="1.5" strokeLinejoin="round" />
        </svg>
      );

    case 'fleece-jacket':
      return (
        <svg
          id="svg-fleece-jacket"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Jacket Body */}
          <path d="M25 22C25 22 35 18 50 18C65 18 75 22 75 22L85 45C86 48 82 50 78 48L74 41V82C74 85 70 88 65 88H35C30 88 26 85 26 82V41L22 48C18 50 14 48 15 45L25 22Z" fill="#4B5563" />
          {/* Collar/Zipper Neck */}
          <path d="M40 18H60V32C60 32 50 36 40 32V18Z" fill="#374151" />
          {/* Zipper details */}
          <path d="M50 22V55" stroke="#9CA3AF" strokeWidth="3" strokeLinecap="round" />
          <rect x="48.5" y="32" width="3" height="6" rx="1" fill="#D1D5DB" />
          {/* Zipper Pull Tab */}
          <circle cx="50" cy="40" r="2" fill="#D1D5DB" />
          {/* Left / Right Pockets */}
          <rect x="30" y="62" width="12" height="10" rx="2" fill="#374151" />
          <rect x="58" y="62" width="12" height="10" rx="2" fill="#374151" />
        </svg>
      );

    case 'onesie':
      return (
        <svg
          id="svg-onesie"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Red Baby Onesie Body */}
          <path d="M30 20C30 18 36 16 50 16C64 16 70 18 70 20L78 35C79 38 74 40 72 38V68C72 72 65 76 65 80C65 82 60 84 50 84C40 84 35 82 35 80C35 76 28 72 28 68V38L26 40C24 41 19 38 20 35L30 20Z" fill="#DC2626" />
          {/* Lap Shoulders & Neckline */}
          <path d="M40 16C40 22 60 22 60 16" stroke="#991B1B" strokeWidth="2.5" />
          {/* Trim accents */}
          <path d="M35 80C35 80 43 78 50 78C57 78 65 80 65 80" stroke="#EF4444" strokeWidth="2" />
          {/* Snap Buttons at bottom */}
          <circle cx="43" cy="81" r="2.5" fill="#E5E7EB" stroke="#9CA3AF" strokeWidth="1" />
          <circle cx="50" cy="81" r="2.5" fill="#E5E7EB" stroke="#9CA3AF" strokeWidth="1" />
          <circle cx="57" cy="81" r="2.5" fill="#E5E7EB" stroke="#9CA3AF" strokeWidth="1" />
          {/* Cute Milk Bottle graphic inside */}
          <rect x="45" y="42" width="10" height="18" rx="2" fill="white" opacity="0.8" />
          <rect x="47" y="38" width="6" height="4" rx="1" fill="#F87171" />
        </svg>
      );

    case 'red-tshirt':
      return (
        <svg
          id="svg-red-tshirt"
          className={`${className} ${transformClass} bg-slate-100 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Red T-shirt Outline */}
          <path d="M25 25C25 22 35 20 50 20C65 20 75 22 75 25L82 42C82 44 78 46 75 44L72 38V76C72 79 68 82 64 82H36C32 82 28 79 28 76V38L25 44C22 46 18 44 18 42L25 25Z" fill="#DC2626" />
          {/* Neckline */}
          <path d="M42 20C42 24 58 24 58 20" stroke="#991B1B" strokeWidth="3" strokeLinecap="round" />
          {/* Robot Outline Logo (allTheThings) */}
          <rect x="44" y="38" width="12" height="12" rx="2.5" fill="white" />
          <circle cx="48" cy="43" r="1.5" fill="#DC2626" />
          <circle cx="52" cy="43" r="1.5" fill="#DC2626" />
          <path d="M47 48H53" stroke="#DC2626" strokeWidth="1.5" strokeLinecap="round" />
          <rect x="48" y="50" width="4" height="6" rx="1" fill="white" />
          {/* Robot Antennas */}
          <path d="M46 38L44 34" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          <path d="M54 38L56 34" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );

    case 'dog-bug':
    default:
      return (
        <svg
          id="svg-dog-bug"
          className={`${className} ${transformClass} bg-red-50 border-2 border-red-300 rounded-lg p-4 transition-transform duration-300`}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Cute Beagle/Puppy Dog representing sl-404 bug avatar */}
          <rect x="0" y="0" width="100" height="100" fill="#FEF2F2" rx="8" />
          {/* Dog Ears */}
          <path d="M22 30C22 20 12 40 16 55C18 62 26 55 26 45V30Z" fill="#78350F" />
          <path d="M78 30C78 20 88 40 84 55C82 62 74 55 74 45V30Z" fill="#78350F" />
          {/* Dog Head */}
          <circle cx="50" cy="45" r="24" fill="#D97706" />
          {/* Eye patches */}
          <circle cx="42" cy="42" r="8" fill="#78350F" />
          {/* Dog Eyes */}
          <circle cx="42" cy="42" r="4" fill="black" />
          <circle cx="58" cy="42" r="4" fill="black" />
          {/* Sparkles */}
          <circle cx="40.5" cy="40.5" r="1" fill="white" />
          <circle cx="56.5" cy="40.5" r="1" fill="white" />
          {/* Snout */}
          <ellipse cx="50" cy="54" rx="10" ry="7" fill="#FEF3C7" />
          {/* Nose */}
          <polygon points="46,51 54,51 50,56" fill="black" />
          {/* Tongue/Mouth */}
          <path d="M47 56C47 60 53 60 53 56" stroke="black" strokeWidth="1.5" strokeLinecap="round" />
          <path d="M50 58C50 62 52 62 52 58" fill="#F87171" />
          {/* Red Space/Hero T-Shirt collar */}
          <path d="M35 65C35 65 40 74 50 74C60 74 65 65 65 65" stroke="#DC2626" strokeWidth="8" strokeLinecap="round" />
          {/* 404 Text */}
          <text x="50" y="85" fill="#EF4444" fontSize="11" fontWeight="bold" textAnchor="middle" fontFamily="monospace">
            BUG 404
          </text>
        </svg>
      );
  }
};
