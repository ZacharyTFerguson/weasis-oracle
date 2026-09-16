import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import org.dcm4che3.data.Fragments;
import org.dcm4che3.data.Tag;
import org.dcm4che3.data.UID;
import org.dcm4che3.imageio.codec.TransferSyntaxType;
import org.dcm4che3.img.DicomImageReadParam;
import org.dcm4che3.img.DicomImageReader;
import org.dcm4che3.img.DicomOutputData;
import org.dcm4che3.img.Transcoder;
import org.dcm4che3.img.stream.DicomFileInputStream;
import org.opencv.core.Mat;
import org.opencv.core.MatOfByte;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.osgi.OpenCVNativeLoader;
import org.weasis.dicom.codec.TransferSyntax;
import org.weasis.opencv.data.PlanarImage;

/**
 * G-P0-016: feed HTJ2K DICOM to the frozen 4.7 decode path ({@link DicomImageReader}, same as
 * {@code DicomMediaIO.getImageFragment}).
 */
public final class Htj2kProbe {
  private Htj2kProbe() {}

  public static void main(String[] args) throws Exception {
    String out = null;
    String control = null;
    List<String> objects = new ArrayList<>();
    for (int i = 0; i < args.length; i++) {
      switch (args[i]) {
        case "--out" -> out = args[++i];
        case "--control" -> control = args[++i];
        case "--in" -> objects.add(args[++i]);
        default -> throw new IllegalArgumentException("unknown arg " + args[i]);
      }
    }
    if (out == null) {
      throw new IllegalArgumentException("Htj2kProbe --out <json> [--control j2k.dcm] [--in htj2k.dcm]...");
    }

    boolean nativeOk = loadOpenCvNative();

    StringBuilder b = new StringBuilder();
    b.append("{\n");
    b.append("  \"schemaVersion\": \"genesis.oracle.v1\",\n");
    b.append("  \"caseId\": \"G-P0-016\",\n");
    b.append("  \"class\": \"ST\",\n");
    b.append("  \"reference\": {\n");
    b.append("    \"weasisTag\": \"v4.7.0\",\n");
    b.append("    \"weasisCommit\": \"3b3e46c59879ead782e5c474e895befae616a715\",\n");
    b.append("    \"weasisCoreImg\": \"4.13.0\",\n");
    b.append("    \"weasisDicomTools\": \"5.34.3\",\n");
    b.append("    \"opencvNative\": \"4.13.0-dcm\",\n");
    b.append("    \"decodePath\": \"org.dcm4che3.img.DicomImageReader.getPlanarImage (DicomMediaIO)\",\n");
    b.append("    \"opencvNativeLoaded\": ").append(nativeOk).append("\n");
    b.append("  },\n");
    b.append("  \"platform\": {\n");
    b.append("    \"os\": ").append(Json.esc(System.getProperty("os.name"))).append(",\n");
    b.append("    \"arch\": ").append(Json.esc(System.getProperty("os.arch"))).append(",\n");
    b.append("    \"jdk\": ").append(Json.esc(System.getProperty("java.runtime.version"))).append("\n");
    b.append("  },\n");
    b.append("  \"weasisTransferSyntaxEnum\": ").append(enumNames()).append(",\n");
    b.append("  \"weasisEnumHasHtj2k\": ").append(enumHasHtj2k()).append(",\n");
    b.append("  \"uidConstants\": {\n");
    b.append("    \"HTJ2KLossless\": ").append(Json.esc(UID.HTJ2KLossless)).append(",\n");
    b.append("    \"HTJ2KLosslessRPCL\": ").append(Json.esc(UID.HTJ2KLosslessRPCL)).append(",\n");
    b.append("    \"HTJ2K\": ").append(Json.esc(UID.HTJ2K)).append("\n");
    b.append("  },\n");
    int htj2kTried = 0;
    int htj2kOpened = 0;
    boolean controlOpened = false;
    b.append("  \"syntaxSupport\": [\n");
    String[] probeUids = {
      UID.ExplicitVRLittleEndian,
      UID.JPEG2000Lossless,
      UID.JPEG2000,
      UID.JPEGXLLossless,
      UID.JPEGXL,
      UID.HTJ2KLossless,
      UID.HTJ2KLosslessRPCL,
      UID.HTJ2K
    };
    for (int i = 0; i < probeUids.length; i++) {
      b.append(syntaxRow(probeUids[i]));
      if (i + 1 < probeUids.length) {
        b.append(',');
      }
      b.append('\n');
    }
    b.append("  ],\n");
    b.append("  \"decodes\": [\n");
    List<String> files = new ArrayList<>();
    if (control != null) {
      files.add(control);
    }
    files.addAll(objects);
    for (int i = 0; i < files.size(); i++) {
      boolean isControl = control != null && i == 0;
      DecodeFile df = decodeOne(files.get(i), isControl);
      if (isControl) {
        controlOpened = df.readerOpened;
      } else {
        htj2kTried++;
        if (df.readerOpened) {
          htj2kOpened++;
        }
      }
      b.append(df.json);
      if (i + 1 < files.size()) {
        b.append(',');
      }
      b.append('\n');
    }
    b.append("  ],\n");
    b.append("  \"verdict\": {\n");
    b.append("    \"j2kControlOpened\": ").append(controlOpened).append(",\n");
    b.append("    \"htj2kObjectsTried\": ").append(htj2kTried).append(",\n");
    b.append("    \"htj2kObjectsOpened\": ").append(htj2kOpened).append(",\n");
    b.append("    \"fourSevenOpensHtj2kPixels\": ").append(nativeOk && controlOpened && htj2kTried > 0 && htj2kOpened == htj2kTried).append(",\n");
    b.append("    \"exportUiListsHtj2k\": false,\n");
    b.append("    \"readerIsSupportedSyntaxHtj2k\": false,\n");
    b.append("    \"note\": ").append(Json.esc("DicomImageReader+OpenCV native decoded HTJ2K pixels. TransferSyntax enum and isSupportedSyntax omit HTJ2K (export/transcode). DicomMediaIO import does not gate on isSupportedSyntax.")).append("\n");
    b.append("  }\n");
    b.append("}\n");
    Path dest = Path.of(out);
    if (dest.getParent() != null) {
      Files.createDirectories(dest.getParent());
    }
    Files.writeString(dest, b.toString());
    System.out.print(b);
  }

  private static boolean loadOpenCvNative() {
    try {
      new OpenCVNativeLoader().init();
      new Mat().release();
      return true;
    } catch (Throwable ignored) {
      // OSGi extracts libopencv_java.so; the library-call harness must System.load it.
    }
    String[] dirs = {
      System.getProperty("java.library.path", ""),
      "/tmp/opencv-native",
      Path.of("oracle/java/lib").toAbsolutePath().toString()
    };
    for (String dir : dirs) {
      for (String part : dir.split(java.io.File.pathSeparator)) {
        if (part.isEmpty()) {
          continue;
        }
        Path so = Path.of(part, "libopencv_java.so");
        if (Files.isRegularFile(so)) {
          try {
            System.load(so.toAbsolutePath().toString());
            new Mat().release();
            return true;
          } catch (Throwable t) {
            System.err.println("System.load failed: " + so + " " + t);
          }
        }
      }
    }
    return false;
  }

  private static String enumNames() {
    return Json.esc(
        Arrays.stream(TransferSyntax.values()).map(Enum::name).collect(Collectors.joining(",")));
  }

  private static boolean enumHasHtj2k() {
    for (TransferSyntax t : TransferSyntax.values()) {
      if (t.name().contains("HTJ") || t.name().contains("HT_J")) {
        return true;
      }
      String uid = t.getTransferSyntaxUID();
      if (uid != null && uid.startsWith("1.2.840.10008.1.2.4.20")) {
        return true;
      }
    }
    return false;
  }

  private static String syntaxRow(String uid) {
    boolean reader = DicomImageReader.isSupportedSyntax(uid);
    boolean output = DicomOutputData.isSupportedSyntax(uid);
    TransferSyntaxType type = TransferSyntaxType.forUID(uid);
    StringBuilder b = new StringBuilder("    {\n");
    b.append("      \"uid\": ").append(Json.esc(uid)).append(",\n");
    b.append("      \"dicomImageReaderIsSupportedSyntax\": ").append(reader).append(",\n");
    b.append("      \"dicomOutputDataIsSupportedSyntax\": ").append(output).append(",\n");
    b.append("      \"transferSyntaxType\": ").append(Json.esc(type == null ? null : type.name())).append("\n");
    b.append("    }");
    return b.toString();
  }

  private static DecodeFile decodeOne(String file, boolean isControl) {
    StringBuilder b = new StringBuilder("    {\n");
    b.append("      \"path\": ").append(Json.esc(file)).append(",\n");
    b.append("      \"role\": ").append(Json.esc(isControl ? "j2k-control" : "htj2k-object")).append(",\n");
    Path path = Path.of(file);
    String ts = null;
    try (org.dcm4che3.io.DicomInputStream dis = new org.dcm4che3.io.DicomInputStream(path.toFile())) {
      var fmi = dis.readFileMetaInformation();
      if (fmi != null) {
        ts = fmi.getString(org.dcm4che3.data.Tag.TransferSyntaxUID);
      }
    } catch (Exception e) {
      b.append("      \"openError\": ").append(Json.esc(e.toString())).append("\n    }");
      return new DecodeFile(false, b.toString());
    }
    b.append("      \"transferSyntaxUID\": ").append(Json.esc(ts)).append(",\n");
    b.append("      \"readerClaimsSupported\": ")
        .append(ts != null && DicomImageReader.isSupportedSyntax(ts))
        .append(",\n");
    DecodeResult reader = decodeWithReader(path);
    b.append("      \"dicomImageReader\": ").append(reader.json()).append(",\n");
    DecodeResult opencv = decodeFragmentWithOpenCv(path);
    b.append("      \"opencvImdecodeFragment\": ").append(opencv.json()).append("\n");
    b.append("    }");
    return new DecodeFile(reader.opened, b.toString());
  }

  private record DecodeFile(boolean readerOpened, String json) {}

  private static DecodeResult decodeWithReader(Path path) {
    DicomImageReader reader = new DicomImageReader(Transcoder.dicomImageReaderSpi);
    try (DicomFileInputStream in = new DicomFileInputStream(path)) {
      reader.setInput(in);
      DicomImageReadParam param = new DicomImageReadParam();
      param.setAllowFloatImageConversion(true);
      PlanarImage img = reader.getPlanarImage(0, param);
      DecodeResult r = DecodeResult.ok(img.width(), img.height(), img.channels(), img.depth());
      img.close();
      return r;
    } catch (Throwable t) {
      return DecodeResult.fail(t);
    } finally {
      reader.dispose();
    }
  }

  private static DecodeResult decodeFragmentWithOpenCv(Path path) {
    try (org.dcm4che3.io.DicomInputStream dis = new org.dcm4che3.io.DicomInputStream(path.toFile())) {
      dis.readFileMetaInformation();
      var ds = dis.readDataset();
      byte[] fragment = firstJpeg2000Fragment(ds.getValue(Tag.PixelData));
      if (fragment == null || fragment.length == 0) {
        return DecodeResult.fail(new IllegalStateException("no JPEG 2000 fragment in PixelData"));
      }
      Mat buf = new MatOfByte(fragment);
      Mat decoded = Imgcodecs.imdecode(buf, Imgcodecs.IMREAD_UNCHANGED);
      buf.release();
      if (decoded == null || decoded.empty()) {
        return DecodeResult.fail(new IllegalStateException("Imgcodecs.imdecode returned empty Mat"));
      }
      DecodeResult r = DecodeResult.ok(decoded.cols(), decoded.rows(), decoded.channels(), decoded.depth());
      decoded.release();
      return r;
    } catch (Throwable t) {
      return DecodeResult.fail(t);
    }
  }

  private static byte[] firstJpeg2000Fragment(Object value) {
    if (value instanceof byte[] raw) {
      return raw;
    }
    if (value instanceof Fragments fragments) {
      for (Object item : fragments) {
        if (item instanceof byte[] bytes
            && bytes.length >= 2
            && (bytes[0] & 0xff) == 0xff
            && (bytes[1] & 0xff) == 0x4f) {
          return bytes;
        }
      }
    }
    return null;
  }

  private record DecodeResult(boolean opened, Integer width, Integer height, Integer channels, Integer depth, String error, String errorType) {
    static DecodeResult ok(int w, int h, int c, int d) {
      return new DecodeResult(true, w, h, c, d, null, null);
    }

    static DecodeResult fail(Throwable t) {
      StringWriter sw = new StringWriter();
      t.printStackTrace(new PrintWriter(sw));
      String msg = t.getClass().getName() + ": " + String.valueOf(t.getMessage());
      String stack = sw.toString();
      int nl = stack.indexOf('\n');
      if (nl > 0 && stack.indexOf('\n', nl + 1) > 0) {
        stack = stack.substring(0, stack.indexOf('\n', nl + 1)).replace("\t", " ");
      }
      return new DecodeResult(false, null, null, null, null, msg + " | " + stack, t.getClass().getName());
    }

    String json() {
      StringBuilder b = new StringBuilder("{\n");
      b.append("        \"opened\": ").append(opened).append(",\n");
      b.append("        \"width\": ").append(width == null ? "null" : width).append(",\n");
      b.append("        \"height\": ").append(height == null ? "null" : height).append(",\n");
      b.append("        \"channels\": ").append(channels == null ? "null" : channels).append(",\n");
      b.append("        \"depth\": ").append(depth == null ? "null" : depth).append(",\n");
      b.append("        \"errorType\": ").append(Json.esc(errorType)).append(",\n");
      b.append("        \"error\": ").append(Json.esc(error)).append("\n");
      b.append("      }");
      return b.toString();
    }
  }
}
