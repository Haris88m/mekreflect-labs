import test from 'node:test';
import assert from 'node:assert/strict';
import { isFreshAvailability, isAllowedMerchantUrl, isEligibleOffer, eligibleOffers } from './availability.mjs';
const now = Date.parse('2026-10-16T12:00:00Z');
const fixture = () => ({ available: true, price: 12.5, quantity: 3, branchActive: true,
  productAllowed: true, observedAt: '2026-10-16T11:59:00Z', expiresAt: '2026-10-16T12:01:00Z',
  sourceKind: 'TEST_FIXTURE' });
test('an isolated fixture requires explicit opt-in', () => {
  assert.equal(isEligibleOffer(fixture(), 1, now), false);
  assert.equal(isEligibleOffer(fixture(), 1, now, {allowTestFixtures:true}), true);
});
test('expiry is exclusive and source timestamps are never refreshed', () => {
  const f=fixture(); assert.equal(isFreshAvailability(f, Date.parse(f.expiresAt)), false);
  assert.equal(isFreshAvailability(f, now), true);
  assert.equal(f.observedAt, '2026-10-16T11:59:00Z');
});
test('a future observation outside permitted clock skew is refused', () => {
  assert.equal(isFreshAvailability({...fixture(), observedAt:'2026-10-16T12:01:01Z'}, now), false);
});
test('timestamps need explicit timezone and valid calendar dates', () => {
  for (const observedAt of ['2026-10-16T11:59:00', '2026-02-30T00:00:00Z', 2026, {}, null])
    assert.equal(isFreshAvailability({...fixture(), observedAt}, now), false);
});
test('an authorized source needs the configured HTTPS hostname', () => {
  const f={...fixture(), sourceKind:'AUTHORIZED_PARTNER_FEED', sourceAuthorized:true, sourceUrl:'https://feed.example.test/data'};
  assert.equal(isEligibleOffer(f, 1, now), false);
  assert.equal(isEligibleOffer(f, 1, now, {authorizedSourceHosts:['feed.example.test']}), true);
  assert.equal(isAllowedMerchantUrl('https://feed.example.test.evil.test/', ['feed.example.test']), false);
});
test('credentials in source URLs are refused', () => {
  assert.equal(isAllowedMerchantUrl('https://user:secret@feed.example.test/', ['feed.example.test']), false);
});
test('quantity must be representable exactly', () => {
  assert.equal(isEligibleOffer({...fixture(),quantity:2**60},1,now,{allowTestFixtures:true}),false);
});
test('malformed and unavailable records are refused', () => {
  for (const change of [{available:'true'}, {price:NaN}, {quantity:0}, {productAllowed:false}, {branchActive:1}, {demo:true,sourceKind:'AUTHORIZED_PARTNER_FEED'}])
    assert.equal(isEligibleOffer({...fixture(),...change},1,now,{allowTestFixtures:true}),false);
});
test('filter preserves only eligible fixtures without mutating the collection', () => {
  const input=[fixture(), {...fixture(),available:false}];
  assert.equal(eligibleOffers(input,1,now,{allowTestFixtures:true}).length,1);
  assert.equal(input.length,2);
  assert.deepEqual(eligibleOffers(null),[]);
});
