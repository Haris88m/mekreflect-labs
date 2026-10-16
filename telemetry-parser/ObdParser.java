package com.mekreflect.carscan;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class ObdParser {
    private ObdParser() {}

    public static String clean(String raw) {
        if (raw == null) return "";
        return raw.replace("SEARCHING...", "").replace("SEARCHING", "").replace(">", "").replace("\r", " ").replace("\n", " ").trim().replaceAll("\\s+", " ");
    }

    private static int[] bytesAfter(String raw, String header) {
        if (raw == null || raw.length() > 65536) return new int[0];
        for (String line : raw.split("[\\r\\n]+")) {
            String frame = clean(line).toUpperCase(Locale.US);
            if (!frame.matches("[0-9A-F]{2}(?: [0-9A-F]{2})*")) continue;
            if (!frame.startsWith(header + " ")) continue;
            String[] payload = frame.substring(header.length() + 1).split(" ");
            int[] out = new int[payload.length];
            for (int j = 0; j < payload.length; j++) out[j] = Integer.parseInt(payload[j], 16);
            return out;
        }
        return new int[0];
    }

    public static Double rpm(String raw) { int[] b = bytesAfter(raw, "41 0C"); return b.length >= 2 ? ((b[0] * 256.0) + b[1]) / 4.0 : null; }
    public static Integer speedKph(String raw) { int[] b = bytesAfter(raw, "41 0D"); return b.length >= 1 ? b[0] : null; }
    public static Integer coolantC(String raw) { int[] b = bytesAfter(raw, "41 05"); return b.length >= 1 ? b[0] - 40 : null; }
    public static Double engineLoadPct(String raw) { int[] b = bytesAfter(raw, "41 04"); return b.length >= 1 ? b[0] * 100.0 / 255.0 : null; }
    public static Double throttlePct(String raw) { int[] b = bytesAfter(raw, "41 11"); return b.length >= 1 ? b[0] * 100.0 / 255.0 : null; }
    public static Integer intakeTempC(String raw) { int[] b = bytesAfter(raw, "41 0F"); return b.length >= 1 ? b[0] - 40 : null; }
    public static Double controlModuleVoltage(String raw) { int[] b = bytesAfter(raw, "41 42"); return b.length >= 2 ? ((b[0] * 256.0) + b[1]) / 1000.0 : null; }

    public static List<String> dtcs(String raw) {
        List<String> out = new ArrayList<>();
        int[] payload = new int[0];
        for (String header : new String[]{"43", "47", "4A"}) {
            payload = bytesAfter(raw, header);
            if (payload.length > 0) break;
        }
        if (payload.length % 2 != 0) return out;
        for (int j = 0; j < payload.length; j += 2) {
            int a = payload[j], b = payload[j + 1];
            if (a == 0 && b == 0) continue;
            char family = "PCBU".charAt((a >> 6) & 0x03);
            out.add(String.format(Locale.US, "%c%d%X%02X", family, (a >> 4) & 0x03, a & 0x0F, b));
        }
        return out;
    }
}
