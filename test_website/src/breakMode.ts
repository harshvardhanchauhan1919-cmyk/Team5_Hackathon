export const BREAK_MODES = [
  'cart_selector',
  'continue_selector',
  'complete_selector',
  'checkout_delay',
] as const;

export type BreakMode = (typeof BREAK_MODES)[number];

const BREAK_MODE_SET = new Set<string>(BREAK_MODES);

export function getBreakMode(search = window.location.search): BreakMode | null {
  const mode = new URLSearchParams(search).get('break');
  return mode && BREAK_MODE_SET.has(mode) ? (mode as BreakMode) : null;
}

export function isBreakMode(mode: BreakMode, search = window.location.search): boolean {
  return getBreakMode(search) === mode;
}
