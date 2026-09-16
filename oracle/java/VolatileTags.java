import java.util.Set;
import org.dcm4che3.data.Tag;

/**
 * One volatile list for header goldens (G-P0-049 / G-P0-003). Matches
 * {@code docs/oracle/volatile-tags.md}. Pixel bulk is skipped separately.
 */
final class VolatileTags {
  static final Set<Integer> STRIP =
      Set.of(
          Tag.ImplementationClassUID,
          Tag.ImplementationVersionName,
          Tag.InstanceCreationDate,
          Tag.InstanceCreationTime,
          Tag.InstanceCreatorUID,
          Tag.SOPInstanceUID,
          Tag.StudyInstanceUID,
          Tag.SeriesInstanceUID,
          Tag.StudyDate,
          Tag.StudyTime);

  static final Set<Integer> SKIP_PIXEL =
      Set.of(Tag.PixelData, Tag.FloatPixelData, Tag.DoubleFloatPixelData);

  private VolatileTags() {}
}
