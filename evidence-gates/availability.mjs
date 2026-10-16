const CLOCK_SKEW_MS = 60 * 1000;

function toHostSet(value) {
  if (value instanceof Set) return value;
  if (Array.isArray(value)) return new Set(value);
  return new Set();
}
/**
 * A production feed URL is trusted only when its exact hostname is configured
 * server-side for an authorized partner. No host is trusted by default.
 */
export function isAllowedMerchantUrl(value, allowedHosts = new Set()) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && toHostSet(allowedHosts).has(url.hostname);
  } catch {
    return false;
  }
}

/**
 * Freshness is source-defined through an explicit expiry. Signal never invents
 * a universal window and never refreshes an observation timestamp on page load.
 */
export function isFreshAvailability(offer, now = Date.now()) {
  if (!offer?.observedAt || !offer?.expiresAt || !Number.isFinite(now)) return false;
  const observedAt = parseUtcTimestamp(offer.observedAt);
  const expiresAt = parseUtcTimestamp(offer.expiresAt);
  if (!Number.isFinite(observedAt) || !Number.isFinite(expiresAt)) return false;
  if (expiresAt <= observedAt) return false;
  return observedAt <= now + CLOCK_SKEW_MS && now < expiresAt;
}

// Export contract: canonical UTC ISO timestamps, with optional milliseconds.
// Round-trip comparison rejects Date.parse's normalization of impossible dates.
function parseUtcTimestamp(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value)) return NaN;
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) return NaN;
  const canonical = value.includes('.') ? value : value.replace('Z', '.000Z');
  return new Date(parsed).toISOString() === canonical ? parsed : NaN;
}

export function isAuthorizedProductionFeed(offer, options = {}) {
  if (offer?.sourceKind !== "AUTHORIZED_PARTNER_FEED" || offer?.demo === true) {
    return false;
  }
  if (offer?.sourceAuthorized !== true) return false;
  return isAllowedMerchantUrl(offer.sourceUrl, options.authorizedSourceHosts);
}

export function isExplicitTestFixture(offer, options = {}) {
  return options.allowTestFixtures === true && offer?.sourceKind === "TEST_FIXTURE";
}

export function isEligibleOffer(
  offer,
  requestedQuantity = 1,
  now = Date.now(),
  options = {},
) {
  if (!offer || offer.available !== true) return false;
  if (!Number.isFinite(offer.price) || offer.price <= 0) return false;
  if (!Number.isSafeInteger(requestedQuantity) || requestedQuantity < 1) return false;
  if (!Number.isSafeInteger(offer.quantity) || offer.quantity < requestedQuantity) return false;
  if (offer.branchActive !== true || offer.productAllowed !== true) return false;
  if (!isFreshAvailability(offer, now)) return false;

  const trustedSource =
    isAuthorizedProductionFeed(offer, options) ||
    isExplicitTestFixture(offer, options);

  return trustedSource;
}

export function eligibleOffers(
  offers,
  requestedQuantity = 1,
  now = Date.now(),
  options = {},
) {
  if (!Array.isArray(offers)) return [];
  return offers.filter((offer) =>
    isEligibleOffer(offer, requestedQuantity, now, options),
  );
}
