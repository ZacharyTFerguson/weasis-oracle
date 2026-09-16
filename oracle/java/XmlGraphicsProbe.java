import java.awt.geom.Point2D;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.weasis.core.ui.model.graphic.imp.PointGraphic;
import org.weasis.core.ui.model.imp.XmlGraphicModel;
import org.weasis.core.ui.model.layer.LayerType;
import org.weasis.core.ui.model.layer.imp.DefaultLayer;
import org.weasis.core.ui.serialize.XmlSerializer;

/**
 * G-P0-017: does Weasis 4.7 write XML presentation graphics?
 *
 * <p>Builds a non-empty {@link XmlGraphicModel}, then calls {@link
 * XmlSerializer#writePresentation} (the 2D-viewer write path). Empty models are skipped by
 * {@code hasSerializableGraphics()}.
 */
public final class XmlGraphicsProbe {
  private XmlGraphicsProbe() {}

  public static void main(String[] args) throws Exception {
    Path out = Path.of(args.length > 0 ? args[0] : "corpus/goldens/G-P0-017.json");
    PointGraphic pt = new PointGraphic();
    pt.setPts(List.of(new Point2D.Double(4, 4)));
    pt.setLayer(new DefaultLayer(LayerType.DRAW));
    pt.buildShape();
    XmlGraphicModel model = new XmlGraphicModel();
    model.addGraphic(pt);
    boolean serializable = model.hasSerializableGraphics();
    StringWriter writer = new StringWriter();
    XmlSerializer.writePresentation(model, writer);
    String xml = writer.toString();
    boolean wrote = serializable && (xml.contains("<presentation") || xml.contains(":presentation"));
    boolean hasPoint = xml.contains("PointGraphic") || xml.contains("point") || xml.contains("<pts");
    String os = jsonEscape(System.getProperty("os.name", ""));
    String arch = jsonEscape(System.getProperty("os.arch", ""));
    String jdk = jsonEscape(System.getProperty("java.version", ""));
    String json =
        """
        {
          "schemaVersion": "genesis.oracle.v1",
          "caseId": "G-P0-017",
          "class": "ST",
          "reference": {
            "weasisTag": "v4.7.0",
            "weasisCommit": "3b3e46c59879ead782e5c474e895befae616a715"
          },
          "platform": {
            "os": "%s",
            "arch": "%s",
            "jdk": "%s"
          },
          "api": "org.weasis.core.ui.serialize.XmlSerializer.writePresentation(GraphicModel, Writer)",
          "writePresentationMethods": [
            "writePresentation(ImageElement, File)",
            "writePresentation(ImageElement, Writer)",
            "writePresentation(GraphicModel, Writer)"
          ],
          "model": "non-empty XmlGraphicModel + PointGraphic on DRAW layer",
          "hasSerializableGraphics": %s,
          "xmlContainsPresentation": %s,
          "xmlContainsGraphic": %s,
          "xmlBytes": %d,
          "fourSevenWritesXmlGraphics": %s,
          "oP5008Applies": %s,
          "weasisOwnTest": "weasis-core/.../imp/suite/SerializationTest.java"
        }
        """
            .formatted(
                os,
                arch,
                jdk,
                serializable,
                xml.contains("<presentation") || xml.contains(":presentation"),
                hasPoint,
                xml.getBytes(StandardCharsets.UTF_8).length,
                wrote,
                wrote);
    if (out.getParent() != null) {
      Files.createDirectories(out.getParent());
    }
    Files.writeString(out, json, StandardCharsets.UTF_8);
    System.out.print(json);
    if (!wrote) {
      System.err.println("xml was:\n" + xml);
      System.exit(1);
    }
  }

  private static String jsonEscape(String s) {
    return s.replace("\\", "\\\\").replace("\"", "\\\"");
  }
}
