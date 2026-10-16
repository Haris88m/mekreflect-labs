import { isEligibleOffer } from './availability.mjs';
const now = Date.parse('2026-10-16T12:00:00Z');
const sample = { available:true, price:12.5, quantity:3, branchActive:true,
  productAllowed:true, observedAt:'2026-10-16T11:59:00Z', expiresAt:'2026-10-16T12:01:00Z', sourceKind:'TEST_FIXTURE' };
for (const [label, offer] of [['current',sample],['expired',{...sample,expiresAt:'2026-10-16T12:00:00Z'}],['unknown quantity',{...sample,quantity:null}]]) {
  console.log(JSON.stringify({label, eligible:isEligibleOffer(offer,1,now,{allowTestFixtures:true}), dataMode:'synthetic local test fixture'}));
}
