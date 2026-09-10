---
name: CardioCare Practitioner
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#404944'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#707974'
  outline-variant: '#bfc9c3'
  surface-tint: '#2b6954'
  primary: '#003527'
  on-primary: '#ffffff'
  primary-container: '#064e3b'
  on-primary-container: '#80bea6'
  inverse-primary: '#95d3ba'
  secondary: '#006a63'
  on-secondary: '#ffffff'
  secondary-container: '#99efe5'
  on-secondary-container: '#006f67'
  tertiary: '#003623'
  on-tertiary: '#ffffff'
  tertiary-container: '#004f34'
  on-tertiary-container: '#31c98f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b0f0d6'
  primary-fixed-dim: '#95d3ba'
  on-primary-fixed: '#002117'
  on-primary-fixed-variant: '#0b513d'
  secondary-fixed: '#9cf2e8'
  secondary-fixed-dim: '#80d5cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#00504a'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
  metric-stat:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '800'
    lineHeight: 36px
    letterSpacing: -0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 2.5rem
  space-3xl: 3rem
  layout-sidebar: 260px
  layout-sidebar-collapsed: 80px
  gutter-desktop: 1.5rem
  gutter-mobile: 1rem
---

## Brand & Style

This design system embodies clinical precision balanced with empathetic warmth, tailored specifically for cardiovascular medical professionals. The brand persona is authoritative, calm, instructive, and supportive. It mitigates the cognitive fatigue and high-stress environment of clinical practice through serene deep emerald tones, mint accents, and generous spatial rhythm.

The design movement combines **Corporate Modern** with **Soft Ambient Clinical Minimalism**:
- Pristine, high-legibility workspaces that prioritize patient data clarity, vital signs monitoring, and diagnostic telemetry.
- High-contrast, reassuring forest and emerald greens evoke health, restoration, and life, contrasting with warm clinic-neutral backgrounds.
- Intentional reduction of visual friction: interfaces avoid jarring alerts in favor of harmonic indicator badges, smooth elevation curves, and tactile feedback.

## Colors

The palette grounds the interface in deep botanical and oceanic greens, providing high visual comfort during extended clinical screen sessions.

- **Primary (`#064E3B`)**: Deep Spruce / Evergreen. Used for foundational structural surfaces (sidebar, primary navigation headers) and primary actions requiring resolute authority.
- **Secondary (`#0F766E`)**: Teal Forest. Bridges deep container surfaces with interactive states, focus indicators, and secondary keyframes.
- **Tertiary (`#10B981`)**: Radiant Emerald / Mint. Used for affirmative statuses, primary CTA buttons ("Nouvelle Consultation"), active badges, and stable vital sign indicators.
- **Neutral (`#0F172A`)**: Deep Slate Blue-Black. Provides maximum contrast typography while avoiding harsh pure blacks.

### Contextual & Vital Scales
- **Surface Canvas**: `#F8FAFC` to `#F1F5F9` — a soft, warming clinical off-white that prevents screen glare.
- **Surface Card**: `#FFFFFF` with whisper borders (`rgba(15, 23, 42, 0.06)`).
- **Cardiology Alert / Tachycardia**: `#EF4444` (Soft Crimson) paired with `#FEF2F2` background.
- **Caution / Arrhythmia Warning**: `#F59E0B` (Warm Amber) paired with `#FFFBEB` background.
- **Telemetry Info / ECG Pulse**: `#0284C7` (Cyan Blue) paired with `#F0F9FF` background.

## Typography

**Plus Jakarta Sans** is the sole typographical voice across headlines, body copy, and telemetry data. Its gentle geometry, open counters, and high x-height combine medical legibility with modern warmth.

- **Headlines**: Weighted from Semi-Bold (600) to Bold (700). Negative letter-spacing enhances cohesion in practitioner greetings, clinical metrics, and section divisions.
- **Clinical Data & Metrics (`metric-stat`)**: Extra Bold (800) for rapid glanceability of patient queues, consultations tally, ECG heart rates, and blood pressure figures.
- **Labels & Tags**: Uppercase styling is reserved strictly for overline badges and sidebar category labels (e.g., `MENU PRINCIPAL`) at small sizes with elevated tracking (`0.04em`).

## Layout & Spacing

The system implements a persistent clinical navigation architecture anchored by a deep spruce drawer and an open, flexible content canvas.

### Layout Philosophy
- **Sidebar-Canvas Model**: Desktop experiences allocate a fixed `260px` vertical navigation lane on the left side, finished in primary dark spruce `#064E3B`. The operational canvas expands fluidly with dynamic maximum containment for widescreen medical displays.
- **Grid Architecture**: 12-column dynamic fluid grid on desktops (`> 1024px`) with `1.5rem` (`24px`) gutters. On tablet viewports (`768px - 1023px`), the grid transitions to 8 columns and the sidebar reduces to an icon rail (`80px`). On mobile devices (`< 768px`), the workspace collapses into a 4-column flow with a sheet drawer.
- **Rhythm**: Built upon a strict 4px/8px incremental rhythm, ensuring cards, metric containers, and agenda tables align uniformly.

## Elevation & Depth

Visual depth is achieved through **ambient clinical lighting** combined with **subtle hairline bounding strokes**, eliminating visual noise while maintaining clear component boundaries.

- **Level 0 (Flat Canvas)**: Used by the `#F8FAFC` root background. No shadow.
- **Level 1 (Card & Module Resting)**: Pure white `#FFFFFF` surface layered with a hairline border `1px solid rgba(15, 23, 42, 0.05)` and an ambient shadow: `0 1px 3px rgba(6, 78, 59, 0.04), 0 4px 12px rgba(15, 23, 42, 0.03)`.
- **Level 2 (Hover / Interactive Surfaces)**: Deepens the green-tinted shadow: `0 8px 24px rgba(6, 78, 59, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04)`, slightly lifting actionable cards and appointment records.
- **Level 3 (Modals, Prescriptions, Popovers)**: Higher elevation with soft focus: `0 20px 38px rgba(6, 78, 59, 0.12), 0 6px 12px rgba(15, 23, 42, 0.06)`.
- **Active Navigation Indicator**: Flat tonal injection (`#0F766E` at 30-50% alpha) set against the spruce sidebar to establish focus without heavy drop shadows.

## Shapes

The design system adopts a **Rounded (Level 2)** philosophy. This balances the structural rigidity expected of professional medical software with welcoming, human-centric rounded corners.

- **Base Components (Inputs, Chips, Small Buttons)**: `0.5rem` (`8px`) for compact density.
- **Cards, Panels, and Containers (`rounded-lg`)**: `1rem` (`16px`) delivering approachable boundaries.
- **Hero Banners & Patient Detail Sheets (`rounded-xl`)**: `1.5rem` (`24px`) for prominent contextual areas.
- **Status Pills, Avatar Rings, and Quick-Action Chips**: Fully rounded pill shapes (`9999px`) to distinguish categorical metadata and operational states.

## Components

### Buttons
- **Primary Action ("Nouvelle Consultation")**: Fill in `#10B981` (Emerald), text `#FFFFFF` in `label-lg`, with subtle glow shadow `0 4px 14px rgba(16, 185, 129, 0.35)`. Hover scales brightness slightly with an active inset state.
- **Secondary Action ("Gérer mes créneaux")**: Fill `#FFFFFF`, border `1px solid #E2E8F0`, text `#0F172A`, hover background `#F8FAFC`.
- **Sidebar Navigation Buttons**: Full-width pills with `12px 16px` padding. Resting text is `#94A3B8`. Active states feature `#0F766E` (or emerald tinted overlay) with bright `#FFFFFF` text and an icon accent.

### Metric & Statistic Cards
- White `#FFFFFF` base, `1rem` corner radius, hairline border `rgba(15, 23, 42, 0.06)`.
- Features an icon container on the left tinted in pastel theme colors (e.g. Mint `#ECFDF5` for appointments, Soft Teal `#F0FDFA` for total patients) with the corresponding icon in `#0F766E`.
- Bold metric stat numeral (`30px`, weight 800) with a sub-label in `#64748B`.

### Badges & Status Chips
- **Status Pills**: Fully rounded capsules. Example: "Prêt pour consultations" uses a `#ECFDF5` background, `#065F46` text, and a pulsating dot (`#10B981`).
- **Date Header Pills**: `#ECFDF5` background with `#065F46` typography, prefixed by calendar iconography.

### Cards & Patient Lists
- **Appointment Rows**: Horizontal cards, lightly hoverable, containing patient identity, scheduled time badge (`15:15`), appointment nature (e.g., "[Présentiel] - Bilan"), and a secondary action button ("Compte-rendu").
- **Divider Lines**: Ultra-soft `1px solid #F1F5F9`.

### Input Fields & Controls
- **Form Controls**: Surface `#FFFFFF`, border `1px solid #CBD5E1`, transition to `2px solid #10B981` with a `0 0 0 3px rgba(16, 185, 129, 0.15)` focus ring.
- **Checkboxes & Radios**: Emerald `#10B981` active fill with soft white checkmarks, non-selected state `1.5px solid #94A3B8`.