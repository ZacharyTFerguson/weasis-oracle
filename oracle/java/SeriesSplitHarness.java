import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Tag;
import org.dcm4che3.io.DicomInputStream;
import org.weasis.core.api.explorer.model.DataExplorerModel;
import org.weasis.core.api.media.data.Codec;
import org.weasis.core.api.media.data.FileCache;
import org.weasis.core.api.media.data.MediaElement;
import org.weasis.core.api.media.data.MediaReader;
import org.weasis.core.api.media.data.MediaSeries;
import org.weasis.core.api.media.data.TagW;
import org.weasis.dicom.codec.TagD;
import org.weasis.dicom.codec.display.Modality;
import org.weasis.dicom.codec.utils.SplittingModalityRules;
import org.weasis.dicom.codec.utils.SplittingModalityRules.Rule;
import org.weasis.dicom.codec.utils.SplittingRules;
import org.weasis.opencv.data.PlanarImage;

/**
 * Applies Weasis {@link SplittingRules} / {@link Rule#isTagValueMatching} to DICOM files.
 *
 * <p>File tags are read with dcm4che3 (same stack HeaderDump uses). {@code DicomMediaIO} file
 * import is not used here: {@code PatientComparator} calls {@code GuiUtils.getUICore()} and
 * requires Felix/UI. Split tag lists and match logic are Weasis library calls, not a reimplementation.
 */
public final class SeriesSplitHarness {
  public static void main(String[] args) throws Exception {
    Locale.setDefault(Locale.ROOT);
    if (args.length < 2) {
      System.err.println("usage: SeriesSplitHarness <out.json> <file.dcm>...");
      System.exit(2);
    }
    Path out = Path.of(args[0]);
    SplittingRules splittingRules = new SplittingRules();
    List<Loaded> loaded = new ArrayList<>();
    for (int i = 1; i < args.length; i++) {
      File f = new File(args[i]);
      loaded.add(load(f));
    }

    List<List<Integer>> groups = new ArrayList<>();
    for (int i = 0; i < loaded.size(); i++) {
      Loaded cur = loaded.get(i);
      boolean placed = false;
      for (List<Integer> g : groups) {
        Loaded first = loaded.get(g.get(0));
        if (sameSeriesUid(first, cur) && similar(splittingRules, first, cur)) {
          g.add(i);
          placed = true;
          break;
        }
      }
      if (!placed) {
        List<Integer> g = new ArrayList<>();
        g.add(i);
        groups.add(g);
      }
    }

    StringBuilder json = new StringBuilder();
    json.append("{\n");
    json.append("  \"schemaVersion\": \"genesis.oracle.v1\",\n");
    json.append("  \"caseId\": \"G-P0-000\",\n");
    json.append("  \"class\": \"ST\",\n");
    json.append("  \"producer\": \"weasis-library-splitting-rules\",\n");
    json.append("  \"splitEngine\": \"org.weasis.dicom.codec.utils.SplittingRules\",\n");
    json.append("  \"dicomMediaIoFileImport\": \"felix-required (GuiUtils/UICore)\",\n");
    json.append("  \"role\": \"predicate-snapshot-not-grouping-oracle\",\n");
    json.append("  \"groupingOracle\": \"corpus/goldens/G-P0-000-felix.json applySplittingRules\",\n");
    json.append("  \"files\": [\n");
    for (int i = 0; i < loaded.size(); i++) {
      Loaded l = loaded.get(i);
      json.append("    {\"file\":\"")
          .append(esc(l.name))
          .append("\",\"modality\":\"")
          .append(esc(l.modality))
          .append("\",\"seriesUid\":\"")
          .append(esc(l.seriesUid))
          .append("\",\"sop\":\"")
          .append(esc(l.sop))
          .append("\",\"convolutionKernel\":\"")
          .append(esc(l.kernel))
          .append("\"}");
      json.append(i + 1 < loaded.size() ? ",\n" : "\n");
    }
    json.append("  ],\n");
    json.append("  \"groups\": [\n");
    for (int gi = 0; gi < groups.size(); gi++) {
      json.append("    [");
      List<Integer> g = groups.get(gi);
      for (int j = 0; j < g.size(); j++) {
        json.append("\"").append(esc(loaded.get(g.get(j)).name)).append("\"");
        if (j + 1 < g.size()) {
          json.append(", ");
        }
      }
      json.append("]");
      json.append(gi + 1 < groups.size() ? ",\n" : "\n");
    }
    json.append("  ]\n}\n");
    Files.createDirectories(out.getParent() == null ? Path.of(".") : out.getParent());
    Files.writeString(out, json.toString(), StandardCharsets.UTF_8);
    System.out.print(json);
    if (groups.size() < 2) {
      System.err.println("expected ConvolutionKernel split into >=2 groups, got " + groups.size());
      System.exit(1);
    }
  }

  static String splitSortJson(Loaded cur) {
    SplittingRules rules = new SplittingRules();
    Modality m = Modality.getModality(cur.modality);
    SplittingModalityRules splitRules = rules.getSplittingModalityRules(m, Modality.DEFAULT);
    String ruleSet = cur.frames > 1 ? "multiFrame" : "singleFrame";
    List<Rule> list =
        splitRules == null
            ? List.of()
            : (cur.frames > 1 ? splitRules.getMultiFrameRules() : splitRules.getSingleFrameRules());
    List<String> rows = new ArrayList<>();
    boolean all = true;
    for (Rule rule : list) {
      boolean match = rule.isTagValueMatching(cur.media, cur.media);
      if (!match) {
        all = false;
      }
      String kw = rule.getTag().getKeyword();
      if (kw == null) {
        kw = rule.getTag().toString();
      }
      rows.add(
          "{\"tag\": "
              + jsonEsc(kw)
              + ", \"selfMatch\": "
              + match
              + "}");
    }
    rows.sort(String::compareTo);
    StringBuilder b = new StringBuilder();
    b.append("{\n");
    b.append("    \"status\": \"library\",\n");
    b.append("    \"engine\": \"org.weasis.dicom.codec.utils.SplittingRules\",\n");
    b.append("    \"api\": \"org.weasis.dicom.codec.utils.SplittingModalityRules.Rule.isTagValueMatching\",\n");
    b.append("    \"dicomModelApplySplittingRules\": \"felix-required\",\n");
    b.append("    \"modality\": ").append(jsonEsc(cur.modality)).append(",\n");
    b.append("    \"frames\": ").append(cur.frames).append(",\n");
    b.append("    \"ruleSet\": ").append(jsonEsc(ruleSet)).append(",\n");
    b.append("    \"ruleCount\": ").append(list.size()).append(",\n");
    b.append("    \"selfMatchAll\": ").append(all).append(",\n");
    b.append("    \"selfMatch\": [");
    for (int i = 0; i < rows.size(); i++) {
      if (i > 0) {
        b.append(", ");
      }
      b.append(rows.get(i));
    }
    b.append("]\n  }");
    return b.toString();
  }

  private static String jsonEsc(String s) {
    return "\"" + esc(s) + "\"";
  }

  /** Library-path MediaElement for DumpMain split/sort (same MapReader as the multi-file harness). */
  static Loaded load(File f) throws IOException {
    Attributes ds;
    try (DicomInputStream in = new DicomInputStream(new FileInputStream(f))) {
      in.readFileMetaInformation();
      ds = in.readDataset();
    }
    Map<TagW, Object> tags = new HashMap<>();
    for (int tag : ds.tags()) {
      TagW tw = TagD.getNullable(tag);
      if (tw == null) {
        continue;
      }
      String[] vals = ds.getStrings(tag);
      if (vals == null || vals.length == 0) {
        continue;
      }
      tags.put(tw, vals.length == 1 ? vals[0] : vals);
    }
    int frames = ds.getInt(Tag.NumberOfFrames, 1);
    MapReader reader = new MapReader(f.toURI(), tags, frames);
    MediaElement media = new MediaElement(reader, null);
    return new Loaded(
        f.getName(),
        str(media, Tag.SeriesInstanceUID),
        str(media, Tag.SOPInstanceUID),
        str(media, Tag.Modality),
        str(media, Tag.ConvolutionKernel),
        frames,
        media);
  }

  private static boolean sameSeriesUid(Loaded a, Loaded b) {
    return a.seriesUid != null && a.seriesUid.equals(b.seriesUid);
  }

  private static boolean similar(SplittingRules rules, Loaded first, Loaded neu) {
    Modality m = Modality.getModality(first.modality);
    SplittingModalityRules splitRules = rules.getSplittingModalityRules(m, Modality.DEFAULT);
    if (splitRules == null) {
      return true;
    }
    List<Rule> list =
        first.frames > 1 ? splitRules.getMultiFrameRules() : splitRules.getSingleFrameRules();
    for (Rule rule : list) {
      if (!rule.isTagValueMatching(first.media, neu.media)) {
        return false;
      }
    }
    return true;
  }

  private static String str(MediaElement media, int tag) {
    Object v = media.getTagValue(TagD.get(tag));
    return v == null ? "" : String.valueOf(v);
  }

  private static String esc(String s) {
    if (s == null) {
      return "";
    }
    return s.replace("\\", "\\\\").replace("\"", "\\\"");
  }

  static final class Loaded {
    final String name;
    final String seriesUid;
    final String sop;
    final String modality;
    final String kernel;
    final int frames;
    final MediaElement media;

    Loaded(
        String name,
        String seriesUid,
        String sop,
        String modality,
        String kernel,
        int frames,
        MediaElement media) {
      this.name = name;
      this.seriesUid = seriesUid;
      this.sop = sop;
      this.modality = modality;
      this.kernel = kernel;
      this.frames = frames;
      this.media = media;
    }
  }

  private static final class MapReader implements MediaReader<MediaElement> {
    private final URI uri;
    private final Map<TagW, Object> tags;
    private final int frames;
    private final FileCache cache = new FileCache(this);

    MapReader(URI uri, Map<TagW, Object> tags, int frames) {
      this.uri = uri;
      this.tags = tags;
      this.frames = frames;
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
    public MediaElement[] getMediaElement() {
      return new MediaElement[0];
    }

    @Override
    public MediaSeries<MediaElement> getMediaSeries() {
      return null;
    }

    @Override
    public boolean delegate(DataExplorerModel explorerModel) {
      return false;
    }

    @Override
    public MediaElement getPreview() {
      return null;
    }

    @Override
    public PlanarImage getImageFragment(MediaElement media) {
      return null;
    }

    @Override
    public int getMediaElementNumber() {
      return frames;
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
  }
}
