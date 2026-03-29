/**
 * Theme Tokens — Exported from Stitch MCP "Luminous Intelligence" Design System
 * Use these constants for dynamic/inline styles and Tailwind config extensions.
 * Always keep in sync with design-tokens.css.
 */

export const colors = {
  primary: '#81ecff',
  primaryContainer: '#00e3fd',
  primaryDim: '#00d4ec',
  onPrimary: '#005762',
  onPrimaryContainer: '#004d57',
  inversePrimary: '#006976',

  secondary: '#ac89ff',
  secondaryContainer: '#7000ff',
  secondaryDim: '#874cff',
  onSecondary: '#290067',
  onSecondaryContainer: '#f8f1ff',

  tertiary: '#aeffd4',
  tertiaryContainer: '#00feb1',
  tertiaryDim: '#00eea6',
  onTertiary: '#006544',
  onTertiaryContainer: '#005c3e',

  error: '#ff716c',
  errorContainer: '#9f0519',
  errorDim: '#d7383b',
  onError: '#490006',
  onErrorContainer: '#ffa8a3',

  background: '#0a0f13',
  onBackground: '#f3f7fd',
  surface: '#0a0f13',
  surfaceBright: '#252d33',
  surfaceDim: '#0a0f13',
  surfaceContainer: '#141a1f',
  surfaceContainerHigh: '#1a2026',
  surfaceContainerHighest: '#1f272c',
  surfaceContainerLow: '#0e1418',
  surfaceContainerLowest: '#000000',
  surfaceTint: '#81ecff',
  surfaceVariant: '#1f272c',
  onSurface: '#f3f7fd',
  onSurfaceVariant: '#a7abb1',
  inverseSurface: '#f6faff',
  inverseOnSurface: '#51565a',

  outline: '#71767b',
  outlineVariant: '#43484d',

  // Semantic
  success: '#aeffd4',
  successDim: '#00eea6',
  successContainer: '#00feb1',
  warning: '#f59e0b',
  warningContainer: '#78350f',
  skillMatched: '#aeffd4',
  skillMissing: '#ff716c',
  skillNeutral: '#43484d',
  scoreHigh: '#aeffd4',
  scoreMedium: '#81ecff',
  scoreLow: '#ff716c',
} as const;

export const fonts = {
  headline: "'Space Grotesk', sans-serif",
  body: "'Inter', sans-serif",
  label: "'Manrope', sans-serif",
} as const;

export const fontSizes = {
  displayLg: '3.5rem',
  displayMd: '2.75rem',
  displaySm: '2.25rem',
  headlineLg: '2rem',
  headlineMd: '1.75rem',
  headlineSm: '1.5rem',
  titleLg: '1.375rem',
  titleMd: '1.125rem',
  titleSm: '0.875rem',
  bodyLg: '1rem',
  bodyMd: '0.875rem',
  bodySm: '0.75rem',
  labelLg: '0.875rem',
  labelMd: '0.75rem',
  labelSm: '0.6875rem',
} as const;

export const spacing = {
  0: '0',
  1: '0.125rem',
  2: '0.25rem',
  3: '0.375rem',
  4: '0.5rem',
  5: '0.625rem',
  6: '0.75rem',
  8: '1rem',
  10: '1.25rem',
  12: '1.5rem',
  16: '2rem',
  20: '2.5rem',
  24: '3rem',
  32: '4rem',
  40: '5rem',
} as const;

export const radius = {
  none: '0',
  xs: '0.125rem',
  sm: '0.25rem',
  md: '0.375rem',
  lg: '0.75rem',
  xl: '1rem',
  '2xl': '1.5rem',
  full: '9999px',
} as const;

export const shadows = {
  sm: '0 1px 3px rgba(0, 227, 253, 0.04)',
  md: '0 4px 12px rgba(0, 227, 253, 0.06)',
  lg: '0 12px 32px rgba(0, 227, 253, 0.08)',
  xl: '0 20px 40px rgba(0, 227, 253, 0.08)',
  glowPrimary: '0 0 20px rgba(129, 236, 255, 0.15)',
  glowSuccess: '0 0 20px rgba(174, 255, 212, 0.15)',
  glowError: '0 0 20px rgba(255, 113, 108, 0.15)',
} as const;

export const glass = {
  bg: 'rgba(31, 39, 44, 0.3)',
  border: 'rgba(67, 72, 77, 0.2)',
  blur: '24px',
  bgHeavy: 'rgba(31, 39, 44, 0.6)',
} as const;

export const transitions = {
  fast: '150ms ease',
  base: '250ms ease',
  slow: '400ms ease',
  spring: '500ms cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const;

export const gradients = {
  primary: 'linear-gradient(135deg, #81ecff, #00e3fd)',
  secondary: 'linear-gradient(135deg, #ac89ff, #7000ff)',
  tertiary: 'linear-gradient(135deg, #aeffd4, #00feb1)',
  surface: 'linear-gradient(180deg, #141a1f, #0a0f13)',
} as const;

/** Tailwind config extension — spread into tailwind.config.ts extend section */
export const tailwindExtend = {
  colors: {
    brand: {
      primary: colors.primary,
      'primary-container': colors.primaryContainer,
      'primary-dim': colors.primaryDim,
      secondary: colors.secondary,
      'secondary-container': colors.secondaryContainer,
      tertiary: colors.tertiary,
      'tertiary-container': colors.tertiaryContainer,
      error: colors.error,
      'error-container': colors.errorContainer,
      success: colors.success,
      'success-container': colors.successContainer,
      warning: colors.warning,
    },
    surface: {
      DEFAULT: colors.surface,
      bright: colors.surfaceBright,
      container: colors.surfaceContainer,
      'container-high': colors.surfaceContainerHigh,
      'container-highest': colors.surfaceContainerHighest,
      'container-low': colors.surfaceContainerLow,
      'container-lowest': colors.surfaceContainerLowest,
      variant: colors.surfaceVariant,
    },
    content: {
      DEFAULT: colors.onSurface,
      variant: colors.onSurfaceVariant,
      inverse: colors.inverseOnSurface,
    },
    outline: {
      DEFAULT: colors.outline,
      variant: colors.outlineVariant,
    },
    skill: {
      matched: colors.skillMatched,
      missing: colors.skillMissing,
      neutral: colors.skillNeutral,
    },
  },
  fontFamily: {
    headline: ['Space Grotesk', 'sans-serif'],
    body: ['Inter', 'sans-serif'],
    label: ['Manrope', 'sans-serif'],
  },
  borderRadius: {
    xs: radius.xs,
    sm: radius.sm,
    md: radius.md,
    lg: radius.lg,
    xl: radius.xl,
    '2xl': radius['2xl'],
  },
  boxShadow: {
    glow: shadows.glowPrimary,
    'glow-success': shadows.glowSuccess,
    'glow-error': shadows.glowError,
    cyan: shadows.lg,
  },
} as const;
