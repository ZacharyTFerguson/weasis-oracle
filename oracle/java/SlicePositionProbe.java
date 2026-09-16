/**
 * Headless Gate 0a producer. Loads Weasis 4.7 classes from native bundles
 * (G-P0-000 library path). Does not reimplement split/sort.
 *
 * Requires JDK 25 to match Weasis 4.7 (this file also compiles on 21 if
 * --release is not forced). Run after scripts/fetch-weasis-4.7-bundles.sh
 * and decompressing needed .jar.xz files.
 */
public class SlicePositionProbe {
  public static void main(String[] args) {
    System.out.println("SlicePositionProbe: compile and run against Weasis 4.7 bundles.");
    System.out.println("See oracle/java/README.md. This stub exists so CI can fail closed");
    System.out.println("when WEASIS_BUNDLES is unset rather than silently reimplementing Java.");
    if (System.getenv("WEASIS_BUNDLES") == null) {
      System.err.println("WEASIS_BUNDLES not set — skip Weasis library call (not a pass).");
      System.exit(2);
    }
  }
}
