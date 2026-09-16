import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Tag;
import org.dcm4che3.io.DicomInputStream;
import org.dcm4che3.util.UIDUtils;
import org.weasis.core.api.media.data.SimpleTaggable;
import org.weasis.core.api.service.WProperties;
import org.weasis.dicom.codec.HiddenSeriesManager;
import org.weasis.dicom.codec.SortSeriesStack;
import org.weasis.dicom.codec.TagD;
import org.weasis.dicom.codec.display.Modality;
import org.weasis.dicom.codec.utils.DicomMediaUtils;
import org.weasis.dicom.codec.utils.SplittingModalityRules;
import org.weasis.dicom.codec.utils.SplittingRules;
import org.weasis.launcher.Utils;

/**
 * Gate 0a producer (G-P0-003). Calls Weasis library APIs. Does not reimplement applySplittingRules.
 *
 * <p>Usage: DumpMain --in file.dcm --out file.json --case-id G-P0-003
 */
public final class DumpMain {
  private DumpMain() {}

  public static void main(String[] args) throws Exception {
    String in = null;
    String out = null;
    String caseId = "G-P0-003";
    for (int i = 0; i < args.length; i++) {
      switch (args[i]) {
        case "--in" -> in = args[++i];
        case "--out" -> out = args[++i];
        case "--case-id" -> caseId = args[++i];
        default -> throw new IllegalArgumentException("unknown arg " + args[i]);
      }
    }
    if (in == null || out == null) {
      throw new IllegalArgumentException("DumpMain --in <dcm> --out <json> [--case-id]");
    }
    Path dest = Path.of(out);
    if (dest.getParent() != null) {
      Files.createDirectories(dest.getParent());
    }
    Files.writeString(dest, dumpOne(new File(in), caseId), StandardCharsets.UTF_8);
  }

  static String dumpOne(File dcm, String caseId) throws IOException {
    Attributes fmi;
    Attributes ds;
    try (DicomInputStream dis = new DicomInputStream(dcm)) {
      fmi = dis.readFileMetaInformation();
      ds = dis.readDataset();
    }

    String header = CanonicalHeader.dump(ds, fmi);
    String headerSha = CanonicalHeader.sha256(header);

    double[] iop = ds.getDoubles(Tag.ImageOrientationPatient);
    double[] ipp = ds.getDoubles(Tag.ImagePositionPatient);
    SimpleTaggable t = new SimpleTaggable();
    if (iop != null && iop.length >= 6) {
      t.setTag(TagD.get(Tag.ImageOrientationPatient), iop);
    }
    if (ipp != null && ipp.length >= 3) {
      t.setTag(TagD.get(Tag.ImagePositionPatient), ipp);
    }
    Double slicePos = DicomMediaUtils.computeSlicePosition(t);

    String uidA = UIDUtils.createUID();
    String uidB = UIDUtils.createUID();
    boolean uidDet = uidA.equals(uidB);

    StringBuilder b = new StringBuilder();
    b.append("{\n");
    b.append("  \"schemaVersion\": \"genesis.oracle.v1\",\n");
    b.append("  \"caseId\": ").append(Json.esc(caseId)).append(",\n");
    b.append("  \"class\": \"ST\",\n");
    b.append("  \"reference\": {\n");
    b.append("    \"weasisTag\": \"v4.7.0\",\n");
    b.append("    \"weasisCommit\": \"3b3e46c59879ead782e5c474e895befae616a715\",\n");
    b.append("    \"weasisCoreImg\": \"4.13.0\",\n");
    b.append("    \"weasisDicomTools\": \"5.34.3\",\n");
    b.append("    \"felixFramework\": \"7.0.5\",\n");
    b.append("    \"opencvNative\": \"4.13.0-dcm\"\n");
    b.append("  },\n");
    b.append("  \"platform\": {\n");
    b.append("    \"os\": ").append(Json.esc(System.getProperty("os.name"))).append(",\n");
    b.append("    \"arch\": ").append(Json.esc(System.getProperty("os.arch"))).append(",\n");
    b.append("    \"jdk\": ").append(Json.esc(System.getProperty("java.runtime.version"))).append("\n");
    b.append("  },\n");
    b.append("  \"slicePosition\": ").append(Json.num(slicePos)).append(",\n");
    b.append("  \"storedPixelData\": ").append(storedPixelJson(ds)).append(",\n");
    b.append("  \"rawFrame\": ").append(decodedFrameJson(dcm)).append(",\n");
    b.append("  \"header\": {\n");
    b.append("    \"projection\": \"canonical-minus-volatile\",\n");
    b.append("    \"volatileList\": \"docs/oracle/volatile-tags.md\",\n");
    b.append("    \"sha256\": ").append(Json.esc(headerSha)).append(",\n");
    b.append("    \"text\": ").append(Json.esc(header)).append("\n");
    b.append("  },\n");
    b.append("  \"splitSort\": ").append(SeriesSplitHarness.splitSortJson(SeriesSplitHarness.load(dcm))).append(",\n");
    b.append("  \"specialElementAttachment\": ").append(attachmentJson(ds)).append(",\n");
    b.append("  \"weasisUrl\": \"weasis://?$dicom:get -l /tmp/study\",\n");
    b.append("  \"weasisUriParse\": ").append(uriParseJson()).append(",\n");
    b.append("  \"localPropertyResolution\": ").append(propertyJson()).append(",\n");
    b.append("  \"splittingRulesSnapshot\": ").append(splittingRulesJson()).append(",\n");
    b.append("  \"sortComparators\": ").append(Json.esc(sortComparatorNames())).append(",\n");
    b.append("  \"uidSynthesis\": {\n");
    b.append("    \"api\": \"org.dcm4che3.util.UIDUtils.createUID\",\n");
    b.append("    \"role\": \"factory-probe-only\",\n");
    b.append("    \"ingestSite\": {\n");
    b.append("      \"sopInstanceUIDMissing\": ").append(Json.esc("DicomMediaIO.writeInstanceTags: header.getString(SOPInstanceUID, String.valueOf(instNb)) — instance number, not createUID")).append(",\n");
    b.append("      \"studySeriesMissing\": ").append(Json.esc("LoadDicom.buildDicomStructure uses TagD.getUID(Level.STUDY) and Tag.SeriesInstanceUID as-is; live Felix dump stores missing Study/Series UID as the string UNKNOWN, not createUID")).append(",\n");
    b.append("      \"createUIDCallSites\": ").append(Json.esc("DicomMediaUtils.createDicomKeyObject; DicomDirLoader.open empty directory; export/print/PR serializers")).append(",\n");
    b.append("      \"createUIDIfNull\": ").append(Json.esc("UIDUtils.createUIDIfNull exists; no org.weasis caller in weasis-dicom-codec / weasis-dicom-explorer jars")).append(",\n");
    b.append("      \"felixDump\": \"corpus/goldens/G-P0-000-felix.json\"\n");
    b.append("    },\n");
    b.append("    \"runA\": ").append(Json.esc(uidA)).append(",\n");
    b.append("    \"runB\": ").append(Json.esc(uidB)).append(",\n");
    b.append("    \"deterministic\": ").append(uidDet).append(",\n");
    b.append("    \"impliedClassForOP1011\": ").append(uidDet ? "\"BE\"" : "\"ST\"").append("\n");
    b.append("  }\n");
    b.append("}\n");
    return b.toString();
  }

  private static String storedPixelJson(Attributes ds) {
    byte[] px;
    try {
      px = ds.getBytes(Tag.PixelData);
    } catch (Exception e) {
      return "null";
    }
    if (px == null || px.length == 0) {
      return "null";
    }
    String sha;
    try {
      sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(px));
    } catch (NoSuchAlgorithmException e) {
      throw new IllegalStateException(e);
    }
    return "{\n    \"sha256\": "
        + Json.esc(sha)
        + ",\n    \"bytes\": "
        + px.length
        + ",\n    \"source\": \"org.dcm4che3.data.Attributes.getBytes(Tag.PixelData)\",\n    \"note\": \"stored bulk, not decoded samples\"\n  }";
  }

  private static String decodedFrameJson(File dcm) {
    try {
      Class.forName("org.opencv.osgi.OpenCVNativeLoader");
    } catch (ClassNotFoundException e) {
      return "{ \"error\": \"opencv not on classpath\" }";
    }
    try {
      new org.opencv.osgi.OpenCVNativeLoader().init();
    } catch (Throwable ignored) {
      Path so = Path.of("/tmp/opencv-native/libopencv_java.so");
      if (java.nio.file.Files.isRegularFile(so)) {
        try {
          System.load(so.toAbsolutePath().toString());
        } catch (Throwable t) {
          return "{ \"error\": " + Json.esc("System.load opencv: " + t) + " }";
        }
      }
    }
    org.dcm4che3.img.DicomImageReader reader =
        new org.dcm4che3.img.DicomImageReader(org.dcm4che3.img.Transcoder.dicomImageReaderSpi);
    try (org.dcm4che3.img.stream.DicomFileInputStream in =
        new org.dcm4che3.img.stream.DicomFileInputStream(dcm.toPath())) {
      reader.setInput(in);
      org.dcm4che3.img.DicomImageReadParam param = new org.dcm4che3.img.DicomImageReadParam();
      param.setAllowFloatImageConversion(true);
      org.weasis.opencv.data.PlanarImage img = reader.getPlanarImage(0, param);
      int w = img.width();
      int h = img.height();
      int ch = img.channels();
      int depth = img.depth();
      long n = (long) w * h * ch;
      String sha;
      int bytes;
      if (depth == org.opencv.core.CvType.CV_16U
          || depth == org.opencv.core.CvType.CV_16S
          || depth == 2) {
        short[] buf = new short[(int) n];
        img.get(0, 0, buf);
        byte[] raw = new byte[buf.length * 2];
        for (int i = 0; i < buf.length; i++) {
          raw[i * 2] = (byte) (buf[i] & 0xff);
          raw[i * 2 + 1] = (byte) ((buf[i] >> 8) & 0xff);
        }
        bytes = raw.length;
        sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw));
      } else {
        byte[] buf = new byte[(int) n];
        img.get(0, 0, buf);
        bytes = buf.length;
        sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(buf));
      }
      img.close();
      return "{\n    \"sha256\": "
          + Json.esc(sha)
          + ",\n    \"bytes\": "
          + bytes
          + ",\n    \"width\": "
          + w
          + ",\n    \"height\": "
          + h
          + ",\n    \"channels\": "
          + ch
          + ",\n    \"depth\": "
          + depth
          + ",\n    \"source\": \"org.dcm4che3.img.DicomImageReader.getPlanarImage\",\n    \"note\": \"decoded typed buffer before Modality LUT\"\n  }";
    } catch (Throwable t) {
      return "{ \"error\": " + Json.esc(String.valueOf(t)) + " }";
    } finally {
      reader.dispose();
    }
  }

  private static String splittingRulesJson() {
    SplittingRules rules = new SplittingRules();
    StringBuilder b = new StringBuilder("{\n    \"source\": \"org.weasis.dicom.codec.utils.SplittingRules\",\n");
    b.append("    \"modalities\": {\n");
    Modality[] mods = {
      Modality.DEFAULT, Modality.CT, Modality.MR, Modality.PT, Modality.US, Modality.XA
    };
    for (int i = 0; i < mods.length; i++) {
      SplittingModalityRules r = rules.getSplittingModalityRules(mods[i], Modality.DEFAULT);
      b.append("      ").append(Json.esc(mods[i].name())).append(": {\n");
      b.append("        \"singleFrameTags\": ").append(ruleTags(r.getSingleFrameRules())).append(",\n");
      b.append("        \"multiFrameTags\": ").append(ruleTags(r.getMultiFrameRules())).append("\n");
      b.append("      }");
      if (i + 1 < mods.length) {
        b.append(',');
      }
      b.append('\n');
    }
    b.append("    }\n  }");
    return b.toString();
  }

  private static String ruleTags(List<SplittingModalityRules.Rule> rules) {
    List<String> names = new ArrayList<>();
    for (SplittingModalityRules.Rule r : rules) {
      names.add(r.getTag().getKeyword() == null ? r.getTag().toString() : r.getTag().getKeyword());
    }
    names.sort(String::compareTo);
    StringBuilder b = new StringBuilder("[");
    for (int i = 0; i < names.size(); i++) {
      if (i > 0) {
        b.append(", ");
      }
      b.append(Json.esc(names.get(i)));
    }
    return b.append(']').toString();
  }

  private static String sortComparatorNames() {
    var vals = SortSeriesStack.getValues();
    StringBuilder b = new StringBuilder();
    for (int i = 0; i < vals.length; i++) {
      if (i > 0) {
        b.append(',');
      }
      b.append(vals[i].toString());
    }
    return b.toString();
  }

  private static String attachmentJson(Attributes ds) {
    String sop = ds.getString(Tag.SOPClassUID, "");
    String series = ds.getString(Tag.SeriesInstanceUID, "");
    HiddenSeriesManager hsm = new HiddenSeriesManager();
    hsm.extractReferencedSeries(ds, series);
    Set<String> refs = new TreeSet<>(hsm.reference2Series.keySet());
    StringBuilder b = new StringBuilder("{\n");
    b.append("    \"status\": \"library\",\n");
    b.append("    \"api\": \"org.weasis.dicom.codec.HiddenSeriesManager.extractReferencedSeries\",\n");
    b.append("    \"dicomModelAttach\": \"felix-required\",\n");
    b.append("    \"sopClassUID\": ").append(Json.esc(sop)).append(",\n");
    b.append("    \"originSeriesUID\": ").append(Json.esc(series)).append(",\n");
    b.append("    \"referencedSeriesCount\": ").append(refs.size()).append(",\n");
    b.append("    \"referencedSeriesUIDs\": [");
    int i = 0;
    for (String u : refs) {
      if (i++ > 0) {
        b.append(", ");
      }
      b.append(Json.esc(u));
    }
    b.append("],\n");
    b.append("    \"felixDump\": \"corpus/goldens/G-P0-000-felix.json\"\n  }");
    return b.toString();
  }

  private static String propertyJson() {
    String black = WProperties.color2Hexadecimal(java.awt.Color.BLACK, true);
    java.awt.Color roundTrip = WProperties.hexadecimal2Color(black);
    StringBuilder b = new StringBuilder("{\n");
    b.append("    \"status\": \"library\",\n");
    b.append("    \"api\": \"org.weasis.core.api.service.WProperties.color2Hexadecimal\",\n");
    b.append("    \"wpropertiesCtor\": \"needs OSGi FrameworkUtil (AppProperties.getBundleContext); not constructed here\",\n");
    b.append("    \"getBooleanProperty\": \"instance method; live UICore maps in Felix localPropertyProjection\",\n");
    b.append("    \"uiCore\": \"felix-required\",\n");
    b.append("    \"colorBlackHex\": ").append(Json.esc(black)).append(",\n");
    b.append("    \"colorRoundTripRgb\": ").append(roundTrip.getRGB()).append(",\n");
    b.append("    \"inventoryCount\": 114,\n");
    b.append("    \"inventorySource\": \"docs/oracle/weasis-properties.json\",\n");
    b.append("    \"liveMaps\": \"corpus/goldens/G-P0-000-felix.json localPropertyProjection\",\n");
    b.append("    \"felixDump\": \"corpus/goldens/G-P0-000-felix.json\"\n  }");
    return b.toString();
  }

  private static String uriParseJson() {
    String input = "weasis://?$dicom:get -l /tmp/study";
    java.util.regex.Pattern pattern = Utils.getWeasisProtocolPattern();
    boolean match = pattern.matcher(input).matches();
    int index = Utils.getWeasisProtocolIndex(input);
    return "{\n    \"input\": "
        + Json.esc(input)
        + ",\n    \"isWeasisProtocol\": "
        + match
        + ",\n    \"index\": "
        + index
        + ",\n    \"api\": \"org.weasis.launcher.Utils.getWeasisProtocolPattern\",\n    \"pattern\": "
        + Json.esc(pattern.pattern())
        + "\n  }";
  }
}
