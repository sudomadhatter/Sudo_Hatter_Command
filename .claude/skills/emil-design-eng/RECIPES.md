# Fluid Motion & Animation Recipes

Ready-to-build implementations for common web UI interaction patterns. Start from these recipes, then adapt—do not rebuild interaction physics from scratch.

Custom curve tokens:
```css
:root {
  /* Strong ease-out for responsive UI enters */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  /* Strong ease-in-out for moving/morphing on-screen */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  /* iOS-style sheet/drawer curve */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}
```

---

## 1. Button Press Feedback

Applies to any pressable element. Instant feedback confirming the interface heard the user.

```css
.button {
  transition: transform 160ms var(--ease-out);
}

.button:active {
  transform: scale(0.97);
}
```
- `scale()` scales children uniformly (labels, badges, icons), creating a physical tactile click.
- Gate `:hover` separately behind `@media (hover: hover) and (pointer: fine)`.

---

## 2. Dropdown, Popover, Menu, Select

Scales out of its triggering element, not out of thin air.

```css
.popover {
  /* Base UI / Radix supplies CSS variable transform-origin */
  transform-origin: var(--transform-origin, top center);
  transition:
    opacity 200ms var(--ease-out),
    transform 200ms var(--ease-out);
}

.popover[data-starting-style],
.popover[data-ending-style] {
  opacity: 0;
  transform: scale(0.95);
}
```
- Never animate from `scale(0)`. Starting from `scale(0.95)` with `opacity: 0` feels organic.
- **Modals are exempt:** Modals keep `transform-origin: center` because they are centered in the viewport.

---

## 3. Tooltips (Instant Subsequent Hovers)

Tooltips delay before appearing to avoid flicker during rapid pointer traversal. Once one tooltip is open, neighboring tooltips open instantly.

```css
.tooltip {
  transform-origin: var(--transform-origin, bottom center);
  transition:
    transform 125ms var(--ease-out),
    opacity 125ms var(--ease-out);
}

.tooltip[data-starting-style],
.tooltip[data-ending-style] {
  opacity: 0;
  transform: scale(0.97);
}

/* Instant switch across toolbar items */
.toolbar:hover .tooltip {
  transition-duration: 0ms;
  transition-delay: 0ms;
}
```

---

## 4. Modal & Dialog Overlay

Backdrop crossfade with a subtle scale entrance.

```css
.dialog-overlay {
  transition: opacity 250ms var(--ease-out);
}
.dialog-overlay[data-starting-style],
.dialog-overlay[data-ending-style] {
  opacity: 0;
}

.dialog-content {
  transform-origin: center;
  transition:
    transform 250ms var(--ease-out),
    opacity 250ms var(--ease-out);
}
.dialog-content[data-starting-style],
.dialog-content[data-ending-style] {
  opacity: 0;
  transform: scale(0.96);
}
```

---

## 5. Bottom Sheet & Mobile Drawer (Apple Spring)

Uses physical spring dynamics to track finger velocity and snap smoothly.

```tsx
import { motion, AnimatePresence } from 'framer-motion';

export function BottomSheet({ isOpen, onClose, children }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed bottom-0 left-0 right-0 z-50 bg-neutral-900 rounded-t-3xl p-6"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{
              type: 'spring',
              damping: 30,
              stiffness: 300,
              mass: 0.8
            }}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, info) => {
              if (info.offset.y > 120 || info.velocity.y > 500) {
                onClose();
              }
            }}
          >
            <div className="w-12 h-1.5 bg-neutral-700 rounded-full mx-auto mb-4" />
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

---

## 6. Toast Notifications (Sonner Guidelines)

Toasts should enter and exit from the same screen edge, stack with visible depth, and support swipe-to-dismiss without blocking pointer events.

```tsx
import { motion } from 'framer-motion';

export function ToastCard({ id, message, index, onDismiss }) {
  const yOffset = index * -12;
  const scale = 1 - index * 0.05;
  const opacity = index > 2 ? 0 : 1 - index * 0.2;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity, y: yOffset, scale }}
      exit={{ opacity: 0, scale: 0.85, transition: { duration: 0.15 } }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      onDragEnd={(_, info) => {
        if (Math.abs(info.offset.x) > 100) {
          onDismiss(id);
        }
      }}
      className="absolute bottom-6 right-6 w-80 p-4 rounded-xl border border-white/10 bg-neutral-900/90 backdrop-blur-lg shadow-xl cursor-grab active:cursor-grabbing text-sm text-white"
    >
      {message}
    </motion.div>
  );
}
```

---

## 7. Morphing / Shared Layout Transitions

When an element expands into a full view, use layout projection.

```tsx
import { motion } from 'framer-motion';

export function ExpandableCard({ id, title, isExpanded, onToggle }) {
  return (
    <motion.div
      layoutId={`card-${id}`}
      onClick={onToggle}
      className="p-6 rounded-2xl bg-neutral-900 border border-neutral-800 cursor-pointer overflow-hidden"
      transition={{ type: 'spring', stiffness: 350, damping: 28 }}
    >
      <motion.h3 layoutId={`title-${id}`} className="text-lg font-bold text-white">
        {title}
      </motion.h3>
      {isExpanded && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="mt-4 text-neutral-400 text-sm"
        >
          Detailed expanded content rendered with physical spatial continuity.
        </motion.p>
      )}
    </motion.div>
  );
}
```

---

## 8. Accessibility Invariant: prefers-reduced-motion

Never completely disable state communication. Replace spatial movement with instantaneous or gentle crossfades.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Preserve essential opacity transitions for state changes */
  .fade-allowed {
    transition: opacity 150ms ease-out !important;
  }
}
```
