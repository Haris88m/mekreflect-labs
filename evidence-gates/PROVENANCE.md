# Source record

Source repository: Haris88m/Project-Signal, retained private.

Source commit: `2a3fdc99a6b1bb129369db6d69b1100536e84359`.

Original path: `web/lib/availability.mjs`.

Original SHA256: `25a9ee906f540a71862da3f13e63216f1f3f19a3752d4a25e12e14664fbdf1f3`.

availability.mjs was copied from that source. Export changes reject credential-bearing source URLs; require canonical, valid UTC ISO timestamps instead of Date.parse coercion; and require safe integers for quantity. The source-defined expiry, 60-second observation clock skew, strict flags, source-kind distinction and explicit fixture opt-in remain existing implementation.

availability.test.mjs and demo.mjs are new isolated publication harnesses. Tests reproduce three original failures before these changes. The original repository is not changed by this extraction. No customer-facing synthetic catalogue or live service is published. No new blanket licence is assigned.
