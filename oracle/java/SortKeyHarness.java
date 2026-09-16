import java.io.File;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalTime;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Tag;
import org.dcm4che3.img.DicomMetaData;
import org.weasis.core.api.explorer.model.DataExplorerModel;
import org.weasis.core.api.media.data.Codec;
import org.weasis.core.api.media.data.FileCache;
import org.weasis.core.api.media.data.TagW;
import org.weasis.dicom.codec.DcmMediaReader;
import org.weasis.dicom.codec.DicomImageElement;
import org.weasis.dicom.codec.DicomSeries;
import org.weasis.dicom.codec.SortSeriesStack;
import org.weasis.dicom.codec.TagD;
import org.weasis.opencv.data.PlanarImage;

/**
 * Gate 0a dry-run leaf (G-P0-015): calls Weasis {@link SortSeriesStack} comparators. Does not
 * reimplement sort. DicomMediaIO is avoided (needs Felix/UI via PatientComparator).
 */
public final class SortKeyHarness {
  private SortKeyHarness() {}

  public static void main(String[] args) throws Exception {
    Locale.setDefault(Locale.ROOT);
    Path out = args.length > 0 ? Path.of(args[0]) : Path.of("corpus/goldens/G-P0-015.json");
    Files.createDirectories(out.getParent() == null ? Path.of(".") : out.getParent());

    StringBuilder names = new StringBuilder("[");
    var vals = SortSeriesStack.getValues();
    for (int i = 0; i < vals.length; i++) {
      if (i > 0) {
        names.append(", ");
      }
      names.append(esc(vals[i].toString()));
    }
    names.append("]");

    StringBuilder pairs = new StringBuilder("[\n");
    int n = 0;
    n = appendPair(pairs, n, "instanceNumber_low_high", "instanceNumber",
        SortSeriesStack.instanceNumber.compare(elem(Tag.InstanceNumber, 1), elem(Tag.InstanceNumber, 5)));
    n = appendPair(pairs, n, "instanceNumber_high_low", "instanceNumber",
        SortSeriesStack.instanceNumber.compare(elem(Tag.InstanceNumber, 5), elem(Tag.InstanceNumber, 1)));
    n = appendPair(pairs, n, "instanceNumber_equal", "instanceNumber",
        SortSeriesStack.instanceNumber.compare(elem(Tag.InstanceNumber, 7), elem(Tag.InstanceNumber, 7)));
    n = appendPair(pairs, n, "instanceNumber_null_left", "instanceNumber",
        SortSeriesStack.instanceNumber.compare(elem(Tag.InstanceNumber, null), elem(Tag.InstanceNumber, 3)));
    n = appendPair(pairs, n, "slicePosition_back_front", "slicePosition",
        SortSeriesStack.slicePosition.compare(slicePos(-50.0), slicePos(50.0)));
    n = appendPair(pairs, n, "slicePosition_null_left", "slicePosition",
        SortSeriesStack.slicePosition.compare(slicePos(null), slicePos(12.5)));
    n = appendPair(pairs, n, "sliceLocation_low_high", "sliceLocation",
        SortSeriesStack.sliceLocation.compare(elem(Tag.SliceLocation, 10.0), elem(Tag.SliceLocation, 20.0)));
    n = appendPair(pairs, n, "contentTime_early_late", "contentTime",
        SortSeriesStack.contentTime.compare(
            elem(Tag.ContentTime, LocalTime.of(12, 0, 0)),
            elem(Tag.ContentTime, LocalTime.of(12, 0, 5))));
    n = appendPair(pairs, n, "acquisitionTime_early_late", "acquisitionTime",
        SortSeriesStack.acquisitionTime.compare(
            elem(Tag.AcquisitionTime, LocalTime.of(8, 30, 0)),
            elem(Tag.AcquisitionTime, LocalTime.of(8, 30, 30))));
    appendPair(pairs, n, "diffusionBValue_b0_b1000", "diffusionBValue",
        SortSeriesStack.diffusionBValue.compare(elem(Tag.DiffusionBValue, 0.0), elem(Tag.DiffusionBValue, 1000.0)));
    pairs.append("\n  ]");

    String json =
        "{\n"
            + "  \"schemaVersion\": \"genesis.oracle.v1\",\n"
            + "  \"caseId\": \"G-P0-015\",\n"
            + "  \"class\": \"ST\",\n"
            + "  \"reference\": {\n"
            + "    \"weasisTag\": \"v4.7.0\",\n"
            + "    \"weasisCommit\": \"3b3e46c59879ead782e5c474e895befae616a715\",\n"
            + "    \"weasisCoreImg\": \"4.13.0\",\n"
            + "    \"weasisDicomTools\": \"5.34.3\",\n"
            + "    \"felixFramework\": \"7.0.5\",\n"
            + "    \"opencvNative\": \"4.13.0-dcm\"\n"
            + "  },\n"
            + "  \"platform\": {\n"
            + "    \"os\": "
            + esc(System.getProperty("os.name"))
            + ",\n"
            + "    \"arch\": "
            + esc(System.getProperty("os.arch"))
            + ",\n"
            + "    \"jdk\": "
            + esc(System.getProperty("java.runtime.version"))
            + "\n"
            + "  },\n"
            + "  \"sortKey\": {\n"
            + "    \"api\": \"org.weasis.dicom.codec.SortSeriesStack\",\n"
            + "    \"producer\": \"weasis-library\",\n"
            + "    \"comparators\": "
            + names
            + ",\n"
            + "    \"pairs\": "
            + pairs
            + "\n"
            + "  }\n"
            + "}\n";
    Files.writeString(out, json, StandardCharsets.UTF_8);
    System.out.print(json);
  }

  private static int appendPair(StringBuilder b, int index, String id, String key, int cmp) {
    if (index > 0) {
      b.append(",\n");
    }
    b.append("    {\"id\": ")
        .append(esc(id))
        .append(", \"key\": ")
        .append(esc(key))
        .append(", \"cmp\": ")
        .append(Integer.signum(cmp))
        .append("}");
    return index + 1;
  }

  private static DicomImageElement elem(int tag, Object value) {
    Map<TagW, Object> tags = baseTags();
    if (value != null) {
      tags.put(TagD.get(tag), value);
    }
    return new DicomImageElement(new StubReader(tags), 0);
  }

  private static DicomImageElement slicePos(Double value) {
    Map<TagW, Object> tags = baseTags();
    if (value != null) {
      tags.put(TagW.SlicePosition, value);
    }
    return new DicomImageElement(new StubReader(tags), 0);
  }

  private static Map<TagW, Object> baseTags() {
    Map<TagW, Object> tags = new HashMap<>();
    tags.put(TagD.get(Tag.Modality), "CT");
    tags.put(TagD.get(Tag.PixelSpacing), new double[] {1.0, 1.0});
    return tags;
  }

  private static String esc(String s) {
    return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
  }

  private static final class StubReader implements DcmMediaReader {
    private final Map<TagW, Object> tags;
    private final FileCache cache = new FileCache(this);
    private final URI uri = URI.create("data:sort-key-stub");

    StubReader(Map<TagW, Object> tags) {
      this.tags = tags;
    }

    @Override
    public URI getUri() {
      return uri;
    }

    @Override
    public FileCache getFileCache() {
      return cache;
    }

    @Override
    public DicomImageElement[] getMediaElement() {
      return new DicomImageElement[0];
    }

    @Override
    public DicomSeries getMediaSeries() {
      return null;
    }

    @Override
    public boolean delegate(DataExplorerModel explorerModel) {
      return false;
    }

    @Override
    public DicomImageElement getPreview() {
      return null;
    }

    @Override
    public PlanarImage getImageFragment(org.weasis.core.api.media.data.MediaElement media) {
      return null;
    }

    @Override
    public int getMediaElementNumber() {
      return 1;
    }

    @Override
    public String getMediaFragmentMimeType() {
      return "application/dicom";
    }

    @Override
    public Map<TagW, Object> getMediaFragmentTags(Object key) {
      return tags;
    }

    @Override
    public void close() {}

    @Override
    public Codec getCodec() {
      return null;
    }

    @Override
    public String[] getReaderDescription() {
      return new String[0];
    }

    @Override
    public Object getTagValue(TagW tag) {
      return tag == null ? null : tags.get(tag);
    }

    @Override
    public void replaceURI(URI uri) {}

    @Override
    public boolean buildFile(File output) {
      return false;
    }

    @Override
    public void setTag(TagW tag, Object value) {
      if (tag != null) {
        tags.put(tag, value);
      }
    }

    @Override
    public boolean containTagKey(TagW tag) {
      return tags.containsKey(tag);
    }

    @Override
    public void setTagNoNull(TagW tag, Object value) {
      if (value != null) {
        setTag(tag, value);
      }
    }

    @Override
    public java.util.Iterator<Map.Entry<TagW, Object>> getTagEntrySetIterator() {
      return tags.entrySet().iterator();
    }

    @Override
    public Attributes getDicomObject() {
      return new Attributes();
    }

    @Override
    public DicomMetaData getDicomMetaData() {
      return null;
    }

    @Override
    public boolean isEditableDicom() {
      return false;
    }
  }
}
