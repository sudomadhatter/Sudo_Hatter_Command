# Apple Glass Recipes — Production Component Catalog

Copy-paste-ready, typed components implementing Apple's frosted and optical liquid glass design language. Designed strictly for **mobile-first web applications** (Next.js 14/15/16, React 18/19, TailwindCSS, Framer Motion).

---

## 1. `AppleFrostedCard`: Standard Content Card

The universal workhorse for cards, list items, and dashboard panels. Runs at locked 120fps on iPhone ProMotion displays.

```tsx
'use client';

import React from 'react';

interface AppleFrostedCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export function AppleFrostedCard({ 
  children, 
  className = '',
  glow = false
}: AppleFrostedCardProps) {
  return (
    <div className={`
      relative overflow-hidden rounded-3xl
      /* Translucent glass backdrop */
      bg-neutral-900/60 dark:bg-neutral-900/60 bg-white/75
      /* Apple optical formula */
      backdrop-blur-xl backdrop-saturate-180
      /* Sub-pixel physical cut edge */
      border border-white/20 dark:border-white/10
      /* Soft ambient elevation */
      shadow-[0_8px_32px_0_rgba(0,0,0,0.18)]
      /* Prevent Safari layer bleed */
      transform-gpu isolation-isolate
      ${className}
    `}>
      {/* Top rim specular highlight simulating overhead illumination */}
      <div 
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 dark:via-white/20 to-transparent" 
      />

      {/* Optional ambient light reflection */}
      {glow && (
        <div 
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-48 h-48 rounded-full bg-cyan-500/10 blur-3xl"
        />
      )}

      {/* Content wrapper */}
      <div className="relative z-10 p-6">
        {children}
      </div>
    </div>
  );
}
```

---

## 2. `AppleMobileTabBar`: Floating Bottom Navigation Dock

Floating bottom navigation dock with responsive touch interaction. Perfect for mobile iOS web apps, keeping thumb reach ergonomics in mind.

```tsx
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface TabItem {
  id: string;
  label: string;
  icon: React.ReactNode;
}

interface AppleMobileTabBarProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (id: string) => void;
}

export function AppleMobileTabBar({
  tabs,
  activeTab,
  onTabChange
}: AppleMobileTabBarProps) {
  return (
    <div className="fixed bottom-6 inset-x-0 flex justify-center z-50 pointer-events-none px-4">
      <nav 
        aria-label="Mobile Navigation"
        className="
          pointer-events-auto
          relative flex items-center gap-1 p-1.5 rounded-full
          bg-neutral-900/70 dark:bg-neutral-900/70 bg-white/80
          backdrop-blur-2xl backdrop-saturate-180
          border border-white/20 dark:border-white/10
          shadow-[0_12px_40px_0_rgba(0,0,0,0.25)]
          transform-gpu
        "
      >
        {/* Top Specular Rim */}
        <div 
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-4 top-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent" 
        />

        {tabs.map(tab => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                relative px-5 py-2.5 rounded-full text-xs font-semibold
                transition-colors duration-200 ease-out
                flex items-center gap-2 select-none
                ${isActive ? 'text-white' : 'text-neutral-400 hover:text-neutral-200'}
              `}
            >
              {/* Active spring pill indicator */}
              {isActive && (
                <motion.div
                  layoutId="active-glass-tab"
                  transition={{ type: 'spring', stiffness: 450, damping: 35 }}
                  className="
                    absolute inset-0 rounded-full
                    bg-white/15 dark:bg-white/15
                    border border-white/25
                    shadow-[inset_0_1px_1px_rgba(255,255,255,0.3)]
                  "
                />
              )}
              
              <span className="relative z-10">{tab.icon}</span>
              <span className="relative z-10">{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
```

---

## 3. `AppleLiquidPill`: Refractive Floating Action Pill

True optical refraction of live background content using `@samasante/liquid-glass`. Uses mathematical SDF displacement maps that survive WebKit/Safari GPU limits.

```tsx
'use client';

import React from 'react';
import { Glass } from '@samasante/liquid-glass';

interface AppleLiquidPillProps {
  title: string;
  badge?: string;
  actionText?: string;
  onAction?: () => void;
  width?: number;
  height?: number;
}

export function AppleLiquidPill({
  title,
  badge,
  actionText = "Open",
  onAction,
  width = 340,
  height = 60
}: AppleLiquidPillProps) {
  return (
    <div className="fixed bottom-8 inset-x-0 flex justify-center z-50 pointer-events-none px-4">
      <div className="pointer-events-auto">
        <Glass
          width={width}
          height={height}
          radius={height / 2}
          optics={{
            depth: 0.82,         // Edge curvature depth
            curvature: 0.38,     // Convex center magnification
            dispersion: 0.24,    // Apple-style subtle chromatic aberration along rim
            frost: 5,            // Background frosted blur
            sheen: 0.5,          // Specular rim light intensity
            sheenWidth: 0.18,    // Thin physical edge reflection
          }}
        >
          <div className="flex items-center justify-between w-full h-full px-5 text-white">
            <div className="flex items-center gap-3">
              {badge && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-white/20 text-white/90">
                  {badge}
                </span>
              )}
              <span className="text-sm font-semibold tracking-tight text-white/95">
                {title}
              </span>
            </div>

            {actionText && (
              <button
                onClick={onAction}
                className="
                  px-3.5 py-1.5 rounded-full text-xs font-semibold
                  bg-white/20 hover:bg-white/30 active:scale-95
                  border border-white/20 shadow-sm
                  transition-all duration-150
                "
              >
                {actionText}
              </button>
            )}
          </div>
        </Glass>
      </div>
    </div>
  );
}
```

---

## 4. `AppleGlassModalSheet`: Mobile Bottom Sheet

Apple iOS modal presentation with authentic frosted background, pull indicator, and spring physics.

```tsx
'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AppleGlassModalSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function AppleGlassModalSheet({
  isOpen,
  onClose,
  title,
  children
}: AppleGlassModalSheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
          {/* Backdrop blur overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm"
          />

          {/* Frosted Glass Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 32, stiffness: 350 }}
            className="
              relative z-10 w-full max-h-[85vh] overflow-y-auto
              rounded-t-[36px]
              bg-neutral-900/80 dark:bg-neutral-900/80 bg-white/90
              backdrop-blur-2xl backdrop-saturate-180
              border-t border-x border-white/20 dark:border-white/10
              shadow-[0_-12px_48px_0_rgba(0,0,0,0.35)]
              p-6 pb-10
            "
          >
            {/* Grab handle bar */}
            <div className="flex justify-center mb-5">
              <div className="w-10 h-1.5 rounded-full bg-white/30 dark:bg-white/20" />
            </div>

            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white tracking-tight">{title}</h2>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 active:scale-95 flex items-center justify-center text-neutral-300 transition-transform"
              >
                ✕
              </button>
            </div>

            {/* Sheet body */}
            <div className="relative z-10">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
```

---

## 5. `AppleGlassButton`: Micro-Interaction Tactile Glass Control

A micro-interaction button matching Emil Kowalski spring motion standards with sub-pixel beveled borders.

```tsx
'use client';

import React from 'react';

interface AppleGlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'regular' | 'prominent' | 'clear';
}

export function AppleGlassButton({
  children,
  variant = 'regular',
  className = '',
  ...props
}: AppleGlassButtonProps) {
  const variantStyles = {
    regular: 'bg-white/10 hover:bg-white/15 active:bg-white/25 border-white/20 text-white',
    prominent: 'bg-white/25 hover:bg-white/35 active:bg-white/40 border-white/35 text-white font-semibold shadow-lg',
    clear: 'bg-white/5 hover:bg-white/10 active:bg-white/15 border-white/10 text-neutral-200'
  };

  return (
    <button
      className={`
        relative px-5 py-2.5 rounded-full text-sm font-medium
        backdrop-blur-lg backdrop-saturate-180
        border
        shadow-[0_4px_16px_0_rgba(0,0,0,0.12)]
        active:scale-95
        transition-all duration-150 ease-out
        select-none cursor-pointer
        ${variantStyles[variant]}
        ${className}
      `}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </button>
  );
}
```

