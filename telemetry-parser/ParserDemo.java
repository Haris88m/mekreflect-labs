package com.mekreflect.carscan;

public final class ParserDemo {
    public static void main(String[] args) {
        String[] frames = {"41 0C 1A F8", "41 0C 1A\r41 0D 20", "41 0C 20 00"};
        System.out.println("Synthetic offline frames. No device connection or diagnosis.");
        for (String frame : frames) {
            Double rpm = ObdParser.rpm(frame);
            System.out.println(frame.replace('\r', '|') + " -> " + (rpm == null ? "unresolved" : rpm + " RPM"));
        }
    }
}
