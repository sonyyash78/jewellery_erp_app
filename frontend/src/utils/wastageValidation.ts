export type WastageValue = number | '';

/**
 * Check whether wastage has been explicitly entered (>= 0) rather than left blank.
 * Zero (`0` or `"0"`) is valid; blank (`""`, `null`, `undefined`), NaN, and negative values are rejected.
 */
export function isWastageMissing(wastage: unknown): boolean {
  if (wastage === '' || wastage === null || wastage === undefined) return true;
  const num = typeof wastage === 'number' ? wastage : Number(String(wastage).trim());
  return !Number.isFinite(num) || num < 0;
}

/**
 * Validate compulsory wastage (>= 0 allowed) and ensure Touch + Wastage < 100.
 * Returns an error message string if invalid, or null when valid.
 */
export function validateWastage(touch: number | '' | null | undefined, wastage: unknown): string | null {
  if (isWastageMissing(wastage)) {
    return 'Wastage is compulsory (enter 0 or greater)';
  }
  const touchNum = Number(touch) || 0;
  const wastageNum = Number(wastage);
  if (touchNum + wastageNum >= 100) {
    return 'Touch + Wastage must be less than 100 (Touch + Wastage < 100)';
  }
  return null;
}

/**
 * Render `0` visibly inside numeric inputs while keeping blank state empty.
 */
export function formatWastageInputValue(wastage: number | string | null | undefined): string | number {
  if (wastage === '' || wastage === null || wastage === undefined) return '';
  return wastage;
}
