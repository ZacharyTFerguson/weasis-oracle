/** Minimal JSON string/number helpers. No Jackson — keeps the producer on the Weasis CP. */
final class Json {
  private Json() {}

  static String esc(String s) {
    if (s == null) {
      return "null";
    }
    StringBuilder b = new StringBuilder("\"");
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      switch (c) {
        case '"' -> b.append("\\\"");
        case '\\' -> b.append("\\\\");
        case '\n' -> b.append("\\n");
        case '\r' -> b.append("\\r");
        case '\t' -> b.append("\\t");
        default -> {
          if (c < 0x20) {
            b.append(String.format(java.util.Locale.ROOT, "\\u%04x", (int) c));
          } else {
            b.append(c);
          }
        }
      }
    }
    return b.append('"').toString();
  }

  static String num(Double d) {
    if (d == null) {
      return "null";
    }
    if (d.isNaN() || d.isInfinite()) {
      throw new IllegalArgumentException("non-finite: " + d);
    }
    return String.format(java.util.Locale.US, "%.17g", d);
  }
}
