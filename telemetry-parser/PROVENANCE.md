# Source record

Source repository: Haris88m/AI-bluetooth, retained private.

Source commit: `7410ee83a38ba68a1422ac97f88bdda2c0b0ab0e`.

Original path: `app/src/main/java/com/mekreflect/carscan/ObdParser.java`.

Original SHA256: `4919e086d0bed50257d8d9a5b11b08808c66c3cca316560b684cc546dac7ff6d`.

ObdParser.java was copied from that source and then changed in this export. Conversion formulas and public method names are retained. bytesAfter and dtcs were hardened to preserve individual response boundaries, require exact byte tokens, reject odd DTC payload lengths, and bound raw response length. ParserTest.java and ParserDemo.java are newly authored publication harnesses.

The local tests reproduced the old frame-splicing bug before the export correction. Tested with Eclipse Temurin JDK 21.0.12.1 on Windows. The portable JDK was downloaded from the official Adoptium API and matched the package SHA256 from its metadata. It is private tooling, not part of this package.

No claim of hardware safety, production compatibility or independent model evaluation follows from these local tests. No new blanket licence is assigned by this extraction.
