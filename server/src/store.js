import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import bcrypt from 'bcryptjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const dataFile = path.join(here, '..', 'data', 'demo.json');
const id = () => crypto.randomUUID();
const iso = (offset = 0) => new Date(Date.now() + offset * 86400000).toISOString();
const seed = () => {
  const campaigns = [
    ['Clean Water for All', 'clean-water-for-all', 'Bring safe, reliable drinking water to rural communities through wells, filtration and local stewardship.', 'Water', 50000, 34750, '💧'],
    ['Learning Without Limits', 'learning-without-limits', 'Equip children with books, classroom materials and the support to stay curious.', 'Education', 35000, 22900, '📚'],
    ['Community Health Access', 'community-health-access', 'Make essential health screenings and care accessible to families who need them most.', 'Health', 40000, 18400, '🩺'],
    ['A Greener Tomorrow', 'a-greener-tomorrow', 'Restore native habitats and grow resilient, greener neighborhoods together.', 'Environment', 28000, 14600, '🌱'],
    ['Meals That Matter', 'meals-that-matter', 'Connect local kitchens and volunteers to families facing food insecurity.', 'Food security', 22000, 9400, '🥗'],
    ['Safe Homes Initiative', 'safe-homes-initiative', 'Help families rebuild safe, stable homes after severe storms.', 'Housing', 60000, 25300, '🏠']
  ].map((c, i) => ({ id: id(), title: c[0], slug: c[1], description: c[2], category: c[3], target: c[4], raised: 0, seedRaised: 0, icon: c[6], status: i === 5 ? 'PAUSED' : 'ACTIVE', startsAt: iso(-60), endsAt: iso(60 + i * 10), createdAt: iso(-60) }));
  const donors = [
    { id: id(), name: 'Amara Johnson', email: 'amara@example.org', phone: '+1 555 0101', createdAt: iso(-44) },
    { id: id(), name: 'Ethan Chen', email: 'ethan@example.org', phone: '+1 555 0102', createdAt: iso(-39) },
    { id: id(), name: 'Sofia Patel', email: 'sofia@example.org', phone: '+1 555 0103', createdAt: iso(-24) },
    { id: id(), name: 'Noah Williams', email: 'noah@example.org', phone: '+1 555 0104', createdAt: iso(-18) },
    { id: id(), name: 'Grace Kim', email: 'grace@example.org', phone: '+1 555 0105', createdAt: iso(-9) },
    { id: id(), name: 'Oliver Brooks', email: 'oliver@example.org', phone: '+1 555 0106', createdAt: iso(-3) }
  ];
  const donations = [];
  donors.forEach((d, i) => {
    for (let n = 0; n < 2; n++) {
      const campaign = campaigns[(i + n) % campaigns.length];
      const amount = [125, 250, 75, 500, 100, 175][(i + n) % 6];
      campaign.raised += amount;
      const status = (i === 2 && n === 1) ? 'FAILED' : 'SUCCEEDED';
      donations.push({ id: id(), campaignId: campaign.id, donorId: d.id, donorName: d.name, email: d.email, amount, currency: 'USD', status, anonymous: false, transactionRef: `DEMO-${String(41001 + i * 2 + n)}`, createdAt: iso(-i * 4 - n), receiptNumber: status === 'SUCCEEDED' ? `RCP-${new Date().getFullYear()}-${String(1001 + i * 2 + n)}` : null, attempts: [{ attemptNumber: 1, status, reference: `ATT-${String(51001 + i * 2 + n)}`, createdAt: iso(-i * 4 - n) }] });
    }
  });
  const accounts = [{ id: id(), name: 'Alex Morgan', email: 'VVITU@ac.in', password: bcrypt.hashSync('VVITU@123', 10), role: 'ADMIN' }, ...donors.map(d => ({ id: id(), name: d.name, email: d.email, password: bcrypt.hashSync('DonorDemo!23', 10), role: 'DONOR' }))];
  for (const donor of donors) donor.userId = accounts.find(account => account.role === 'DONOR' && account.email.toLowerCase() === donor.email.toLowerCase())?.id;
  return { campaigns, donors, donations, audit: [{ id: id(), action: 'SYSTEM_SEEDED', entity: 'System', entityId: null, actor: 'System', createdAt: iso(-5) }], accounts, refreshTokens: [], notifications: [], loginActivity:[], savedCampaigns:[], followedCampaigns:[], donorPreferences:[], notificationPreferences:[], supportTickets:[], deletionRequests:[], campaignUpdates:[], dashboardPreferences:[], emailVerifications:[], passwordResets:[] };
};
export function readStore() {
  try { const state = JSON.parse(fs.readFileSync(dataFile, 'utf8')); for (const key of ['notifications','savedCampaigns','followedCampaigns','donorPreferences','notificationPreferences','supportTickets','loginActivity','deletionRequests','campaignUpdates','dashboardPreferences','emailVerifications','passwordResets']) state[key] ||= [];const seededEmails=new Set(['amara@example.org','ethan@example.org','sofia@example.org','noah@example.org','grace@example.org','oliver@example.org']);for(const donor of state.donors)if(!donor.userId&&seededEmails.has(donor.email.toLowerCase())){const owner=state.accounts.find(account=>account.role==='DONOR'&&account.email.toLowerCase()===donor.email.toLowerCase());if(owner)donor.userId=owner.id;}return state; }
  catch { const state = seed(); writeStore(state); return state; }
}
export function writeStore(state) {
  fs.mkdirSync(path.dirname(dataFile), { recursive: true });
  fs.writeFileSync(dataFile, JSON.stringify(state, null, 2));
}
export { id };
