import { describe, expect, it } from 'vitest';
import { amountInCents, money } from './money.js';

describe('money helpers', () => {
  it('formats amounts as USD', () => expect(money(1250)).toBe('$1,250'));
  it('converts decimal values to integer cents without floating point', () => {
    expect(amountInCents('15.25')).toBe(1525);
    expect(amountInCents('0.10') + amountInCents('0.20')).toBe(30);
  });
  it('rejects more than two fractional digits', () => expect(amountInCents('1.005')).toBeNull());
});
