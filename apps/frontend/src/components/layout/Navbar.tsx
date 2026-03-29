"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Navbar = () => {
  const pathname = usePathname();

  const isActive = (path: string) => pathname?.startsWith(path);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[var(--stitch-surface)]/80 backdrop-blur-lg border-b border-[var(--stitch-border)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-gradient-to-br from-[var(--stitch-primary)] to-[#8A2BE2] flex items-center justify-center shadow-[var(--stitch-shadow-md)]">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="font-bold text-xl tracking-tight text-[var(--stitch-typography-primary)]">Luminous API</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <Link 
              href="/dashboard" 
              className={`text-sm font-medium transition-colors hover:text-[var(--stitch-primary)] ${isActive('/dashboard') ? 'text-[var(--stitch-primary)]' : 'text-[var(--stitch-typography-secondary)]'}`}
            >
              Dashboard
            </Link>
            <Link 
              href="/profile" 
              className={`text-sm font-medium transition-colors hover:text-[var(--stitch-primary)] ${isActive('/profile') ? 'text-[var(--stitch-primary)]' : 'text-[var(--stitch-typography-secondary)]'}`}
            >
              Profile
            </Link>
            <Link 
              href="/settings" 
              className={`text-sm font-medium transition-colors hover:text-[var(--stitch-primary)] ${isActive('/settings') ? 'text-[var(--stitch-primary)]' : 'text-[var(--stitch-typography-secondary)]'}`}
            >
              Settings
            </Link>

            <div className="h-6 w-px bg-[var(--stitch-border)] mx-2"></div>
            
            <button className="flex items-center gap-2 text-sm font-medium text-[var(--stitch-typography-primary)] hover:text-[var(--stitch-primary)] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] flex items-center justify-center overflow-hidden">
                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=Alex&backgroundColor=transparent`} alt="Avatar" className="w-full h-full object-cover" />
              </div>
              <span>Alex</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
