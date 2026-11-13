export const money = value => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(Number(value) || 0);
export const amountInCents = value => {
  const raw = String(value).trim();
  if (!/^\d+(\.\d{1,2})?$/.test(raw)) return null;
  const [whole, fraction = ''] = raw.split('.');
  return Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
};
