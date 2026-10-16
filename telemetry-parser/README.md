# Offline telemetry parser

I explored diagnostic software because I wanted to understand the difference between a transport being visible and a response actually containing usable information. The useful research question here is smaller than an Android app. Can an incomplete response become a believable number when a parser joins unrelated context?

This is the Java parser from my AI-bluetooth research, extracted into a local lab. The PID conversion formulas are existing source. The public revision isolates response lines and rejects malformed bytes instead of silently borrowing context from a following response. A new offline harness shows a valid frame, an incomplete frame and a valid recovery frame.

## Run

Use a local JDK 17 or newer. No dependencies, network, Android SDK, vehicle or Bluetooth device are required.

```text
javac -d out ObdParser.java ParserTest.java ParserDemo.java
java -cp out com.mekreflect.carscan.ParserTest
java -cp out com.mekreflect.carscan.ParserDemo
```

The test harness runs 17 assertions. The malformed two-line input used to return 1680.25 RPM, even though the first response was missing a byte. It now returns null. The next complete response still decodes normally. Tests cover all seven retained conversion methods, null/truncated/corrupt input, line isolation, DTC families and a response size bound.

## Scope

Input is whitespace-separated hexadecimal response bytes on individual lines. Command echoes and standalone prompts are ignored. CAN headers, ISO-TP assembly, multiple ECU arbitration, checksums, compact hex streams and device transport are not implemented. The first valid matching frame is used; this is not a complete protocol decoder or a diagnosis. The checks use authored synthetic responses, not measurements from a vehicle. No model is invoked by this lab.

The original app and its archives remain separate. This publication contains no APK, radio interface, VIN, physical-device command or historical device log. See PROVENANCE.md for the source identity and changes.
