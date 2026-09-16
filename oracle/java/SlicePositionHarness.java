import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import org.dcm4che3.data.Tag;
import org.weasis.core.api.media.data.SimpleTaggable;
import org.weasis.core.api.media.data.TagW;
import org.weasis.dicom.codec.TagD;
import org.weasis.dicom.codec.utils.DicomMediaUtils;
import org.weasis.dicom.codec.utils.SplittingRules;

/**
 * Gate 0a producer: calls Weasis 4.7 library methods. Does not reimplement split/sort.
 */
public final class SlicePositionHarness {
  public static void main(String[] args) throws Exception {
    Locale.setDefault(Locale.ROOT);
    SimpleTaggable t = new SimpleTaggable();
    t.setTag(TagD.get(Tag.ImageOrientationPatient), new double[] {1, 0, 0, 0, 1, 0});
    t.setTag(TagD.get(Tag.ImagePositionPatient), new double[] {0, 0, 10});
    Double pos = DicomMediaUtils.computeSlicePosition(t);
    Object cached = t.getTagValue(TagW.SlicePosition);

    StringBuilder stack = new StringBuilder("[");
    double[] zs = new double[] {0.0, 10.0, 20.0};
    for (int i = 0; i < zs.length; i++) {
      SimpleTaggable s = new SimpleTaggable();
      s.setTag(TagD.get(Tag.ImageOrientationPatient), new double[] {1, 0, 0, 0, 1, 0});
      s.setTag(TagD.get(Tag.ImagePositionPatient), new double[] {0, 0, zs[i]});
      Double p = DicomMediaUtils.computeSlicePosition(s);
      if (i > 0) {
        stack.append(", ");
      }
      stack.append(p);
    }
    stack.append("]");

    String splitStatus;
    try {
      SplittingRules rules = new SplittingRules();
      splitStatus = "library:" + rules.getClass().getName();
    } catch (Throwable e) {
      splitStatus = "not-library:" + e.getClass().getName() + ":" + String.valueOf(e.getMessage());
    }

    String json =
        "{\n"
            + "  \"schemaVersion\": \"genesis.oracle.v1\",\n"
            + "  \"caseId\": \"G-P0-000\",\n"
            + "  \"class\": \"ST\",\n"
            + "  \"producer\": \"weasis-library\",\n"
            + "  \"slicePosition\": "
            + pos
            + ",\n"
            + "  \"cachedSlicePosition\": "
            + cached
            + ",\n"
            + "  \"sliceStack\": "
            + stack
            + ",\n"
            + "  \"splitRules\": \""
            + escape(splitStatus)
            + "\"\n"
            + "}\n";
    if (args.length > 0) {
      Path out = Path.of(args[0]);
      Files.createDirectories(out.getParent() == null ? Path.of(".") : out.getParent());
      Files.writeString(out, json, StandardCharsets.UTF_8);
    } else {
      System.out.print(json);
    }
    if (pos == null || Math.abs(pos - 10.0) > 1e-9) {
      System.err.println("unexpected slicePosition " + pos);
      System.exit(1);
    }
  }

  private static String escape(String s) {
    return s.replace("\\", "\\\\").replace("\"", "\\\"");
  }
}
