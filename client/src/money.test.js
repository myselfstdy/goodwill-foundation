import { describe, expect, it } from 'vitest';
import { amountInCents, money } from './money.js';

describe('money helpers', () => {
  it('formats suggested and large donation amounts in Indian Rupees', () => { expect([500,1000,10000,100000].map(amount=>money(amount))).toEqual(['₹500.00','₹1,000.00','₹10,000.00','₹1,00,000.00']); expect(money(1250)).toBe('₹1,250.00'); });
  it('preserves historical transaction currency when supplied', () => expect(money(1250, 'USD')).toBe('$1,250.00'));
  it('converts decimal values to integer cents without floating point', () => {
    expect(amountInCents('15.25')).toBe(1525);
    expect(amountInCents('0.10') + amountInCents('0.20')).toBe(30);
  });
  it('rejects more than two fractional digits', () => expect(amountInCents('1.005')).toBeNull());
});
