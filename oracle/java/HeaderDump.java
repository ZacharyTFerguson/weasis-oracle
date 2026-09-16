import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.ElementDictionary;
import org.dcm4che3.data.Tag;
import org.dcm4che3.data.VR;
import org.dcm4che3.io.DicomInputStream;
import org.dcm4che3.util.TagUtils;

/** Header dump via dcm4che3 as shipped inside Weasis 4.7 codec (G-P0-003 / G-P0-052). */
public final class HeaderDump {
  private static final Set<Integer> VOLATILE = VolatileTags.STRIP;

  public static void main(String[] args) throws Exception {
    Locale.setDefault(Locale.ROOT);
    if (args.length < 1) {
      System.err.println("usage: HeaderDump <file.dcm> [out.json]");
      System.exit(2);
    }
    Attributes fmi;
    Attributes ds;
    try (DicomInputStream in = new DicomInputStream(new FileInputStream(args[0]))) {
      fmi = in.readFileMetaInformation();
      ds = in.readDataset();
    }
    List<String> lines = new ArrayList<>();
    dump(lines, fmi, true);
    dump(lines, ds, false);
    Collections.sort(lines);
    StringBuilder json = new StringBuilder();
    json.append("{\n  \"schemaVersion\": \"genesis.oracle.v1\",\n");
    json.append("  \"caseId\": \"G-P0-049\",\n");
    json.append("  \"class\": \"ST\",\n");
    json.append("  \"producer\": \"weasis-dcm4che-header\",\n");
    json.append("  \"projection\": \"canonical-minus-volatile\",\n");
    json.append("  \"tags\": [\n");
    for (int i = 0; i < lines.size(); i++) {
      json.append("    ").append(lines.get(i));
      if (i + 1 < lines.size()) {
        json.append(",");
      }
      json.append("\n");
    }
    json.append("  ]\n}\n");
    if (args.length > 1) {
      Path out = Path.of(args[1]);
      Files.createDirectories(out.getParent() == null ? Path.of(".") : out.getParent());
      Files.writeString(out, json, StandardCharsets.UTF_8);
    } else {
      System.out.print(json);
    }
  }

  private static void dump(List<String> lines, Attributes attrs, boolean fmi) {
    if (attrs == null) {
      return;
    }
    int[] tags = attrs.tags();
    for (int tag : tags) {
      int key = tag;
      if (VOLATILE.contains(key) || VolatileTags.SKIP_PIXEL.contains(key)) {
        continue;
      }
      VR vr = attrs.getVR(tag);
      String kw = ElementDictionary.keywordOf(tag, null);
      String val = attrs.getString(tag, "");
      if (val == null) {
        val = "";
      }
      val = val.replace("\\", "\\\\").replace("\"", "\\\"");
      lines.add(
          "{\"tag\":\""
              + TagUtils.toString(tag)
              + "\",\"kw\":\""
              + kw
              + "\",\"vr\":\""
              + vr
              + "\",\"fmi\":"
              + fmi
              + ",\"value\":\""
              + val
              + "\"}");
    }
  }
}
