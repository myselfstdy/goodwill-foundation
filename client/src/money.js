export const moneyCompact = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', notation: 'compact', maximumFractionDigits: 1 }).format(Number(value) || 0);
export const money = (value, currency = 'INR') => new Intl.NumberFormat(currency === 'INR' ? 'en-IN' : 'en-US', { style: 'currency', currency, minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value) || 0);
export const moneyBreakdown = totals => Object.entries(totals || {}).filter(([, value]) => Number(value) !== 0).sort(([a],[b]) => a === 'INR' ? -1 : b === 'INR' ? 1 : a.localeCompare(b)).map(([currency, value]) => money(value, currency)).join(' · ') || money(0);
export const amountInCents = value => {
  const raw = String(value).trim();
  if (!/^\d+(\.\d{1,2})?$/.test(raw)) return null;
  const [whole, fraction = ''] = raw.split('.');
  return Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
}
