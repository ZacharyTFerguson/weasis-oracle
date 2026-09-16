import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Two DumpMain passes must match after stripping uidSynthesis runA/runB (G-P0-053 / G-P0-051).
 */
public final class DualRunDriver {
  public static void main(String[] args) throws Exception {
    if (args.length < 3) {
      throw new IllegalArgumentException("DualRunDriver <dcm> <outA.json> <outB.json>");
    }
    Path dcm = Path.of(args[0]);
    Path a = Path.of(args[1]);
    Path b = Path.of(args[2]);
    DumpMain.main(new String[] {"--in", dcm.toString(), "--out", a.toString(), "--case-id", "G-P0-003"});
    DumpMain.main(new String[] {"--in", dcm.toString(), "--out", b.toString(), "--case-id", "G-P0-003"});
    String sa = stripUidRuns(Files.readString(a));
    String sb = stripUidRuns(Files.readString(b));
    if (!sa.equals(sb)) {
      System.err.println("determinism fail: dumps differ after UID-probe strip");
      System.exit(1);
    }
    System.out.println("dual-run ok " + dcm.getFileName());
  }

  static String stripUidRuns(String json) {
    return json.replaceAll("\"runA\": \"[^\"]+\"", "\"runA\": \"<stripped>\"")
        .replaceAll("\"runB\": \"[^\"]+\"", "\"runB\": \"<stripped>\"");
  }
}
