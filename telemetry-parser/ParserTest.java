package com.mekreflect.carscan;

import java.util.List;

public final class ParserTest {
    private static int checks;
    private static void equal(Object expected, Object actual, String name) {
        checks++;
        if (!java.util.Objects.equals(expected, actual)) throw new AssertionError(name + ": expected " + expected + ", got " + actual);
    }
    public static void main(String[] args) {
        equal(1726.0, ObdParser.rpm("41 0C 1A F8"), "RPM formula");
        equal(32, ObdParser.speedKph("41 0D 20"), "speed formula");
        equal(60, ObdParser.coolantC("41 05 64"), "temperature offset");
        equal(100.0, ObdParser.engineLoadPct("41 04 FF"), "load maximum");
        equal(0.0, ObdParser.throttlePct("41 11 00"), "throttle minimum");
        equal(24, ObdParser.intakeTempC("41 0F 40"), "intake offset");
        equal(14.0, ObdParser.controlModuleVoltage("41 42 36 B0"), "voltage formula");
        equal(null, ObdParser.rpm(null), "null input");
        equal(null, ObdParser.rpm("41 0C 1A"), "short frame");
        equal(null, ObdParser.rpm("41 0C 1A\r41 0D 20"), "must not borrow next response bytes");
        equal(null, ObdParser.rpm("41 0C 1A ZZ F8"), "must not skip corrupt bytes");
        equal(null, ObdParser.rpm("7E8 04 41 0C 1A F8"), "framed CAN is unsupported");
        equal(1726.0, ObdParser.rpm("010C\rSEARCHING...\r41 0c 1a f8\r>"), "echo and prompt");
        equal(List.of("P0133", "U0123"), ObdParser.dtcs("43 01 33 C1 23 00 00"), "DTC families");
        equal(List.of(), ObdParser.dtcs("43 01 ZZ 33 00"), "corrupt DTC");
        equal(List.of(), ObdParser.dtcs("43 01\r41 0D 20"), "DTC frame isolation");
        equal(null, ObdParser.rpm("X".repeat(65537)), "bounded response");
        System.out.println(checks + " parser checks passed");
    }
}
