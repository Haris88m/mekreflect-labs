# Evidence and expiry gates

I built Signal around a practical distinction. Finding a reference on the web does not establish that a supplier can fulfil it now. Identity, permission, quantity and freshness answer different questions. I wanted the software to keep those questions visible rather than make an uncertain record look complete.

This lab extracts the existing availability module into an offline JavaScript example. The code checks exact booleans, a configured source hostname, source-defined expiry, positive price and sufficient quantity. Test fixtures require an explicit option. The demonstration uses an invented generic item with no customer, health or supplier records.

```text
node --test availability.test.mjs
node demo.mjs
```

Node 22 or newer is recommended. There are no dependencies or external requests. Nine tests exercise freshness boundaries, clock skew, fixture isolation, source identity, malformed values, quantity bounds and non-mutating filtering. Before correction, three tests failed on the original module. The export now refuses ambiguous or impossible timestamps, URLs containing credentials and quantities outside JavaScript's safe integer range.

## How it works

An input record carries observedAt and expiresAt as canonical UTC timestamps, using `YYYY-MM-DDTHH:mm:ssZ` or the same format with three millisecond digits. The gate never refreshes those fields. Exactly at expiry the record is rejected. Observations may be at most 60 seconds ahead of the supplied clock, preserving the original clock-skew policy.

An authorized production-source label requires an explicit source authorization flag and an HTTPS hostname supplied by the caller. This is an assertion check over input, not verification of a contract, trusted timestamp or actual availability. The hostname allowlist is not a network sandbox or SSRF defence; this code does not fetch URLs. Integrating it into a service requires authentication and trusted server-owned policy.

Only the generic decision function is published. Partner files, product references, health guidance, actual prices and the original database remain outside this package. No ordering, payment, reservation or medical action is performed. The original commerce gates are not included and a passing eligibility result is not permission to transact.
