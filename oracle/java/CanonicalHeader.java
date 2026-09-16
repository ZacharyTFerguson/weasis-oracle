import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Sequence;
import org.dcm4che3.data.VR;
import org.dcm4che3.util.TagUtils;

/** Canonical-minus-volatile header dump for DumpMain (G-P0-049 / G-P0-003). */
final class CanonicalHeader {
  private CanonicalHeader() {}

  static String dump(Attributes dataset, Attributes fmi) {
    StringBuilder b = new StringBuilder();
    if (fmi != null) {
      b.append("# File Meta Information\n");
      dumpAttrs(fmi, b, 0);
    }
    b.append("# Dataset\n");
    dumpAttrs(dataset, b, 0);
    return b.toString();
  }

  static String sha256(String text) {
    try {
      byte[] d =
          MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));
      return HexFormat.of().formatHex(d);
    } catch (NoSuchAlgorithmException e) {
      throw new IllegalStateException(e);
    }
  }

  private static void dumpAttrs(Attributes a, StringBuilder b, int indent) {
    for (int tag : a.tags()) {
      if (VolatileTags.SKIP_PIXEL.contains(tag) || VolatileTags.STRIP.contains(tag)) {
        continue;
      }
      VR vr = a.getVR(tag);
      b.append(" ".repeat(indent));
      b.append(TagUtils.toString(tag)).append(' ');
      b.append(vr == null ? "UN" : vr).append(' ');
      if (vr == VR.SQ) {
        Sequence seq = a.getSequence(tag);
        int n = seq == null ? 0 : seq.size();
        b.append(n).append('\n');
        if (seq != null) {
          int i = 0;
          for (Attributes item : seq) {
            b.append(" ".repeat(indent + 2));
            b.append("Item ").append(i++).append('\n');
            dumpAttrs(item, b, indent + 4);
          }
        }
        continue;
      }
      String val;
      try {
        val = a.getString(tag, "");
      } catch (Exception e) {
        val = "<unprintable>";
      }
      if (val == null) {
        val = "";
      }
      String[] ss;
      try {
        ss = a.getStrings(tag);
      } catch (Exception e) {
        ss = new String[] {val};
      }
      int vm = ss == null ? 0 : ss.length;
      b.append(vm).append(' ');
      if (vm == 0) {
        b.append('\n');
      } else if (vm == 1) {
        b.append(val).append('\n');
      } else {
        b.append(String.join("\\", ss)).append('\n');
      }
    }
  }
}
