# XML graphics write (G-P0-017)

**Present in Weasis 4.7.** `O-P5-008` applies. Do not strike.

## Evidence

| Kind | Where |
| --- | --- | --- |
| Write API | `org.weasis.core.ui.serialize.XmlSerializer.writePresentation` (File and Writer overloads) on SHA `3b3e46c59879ead782e5c474e895befae616a715` |
| JAXB model | `org.weasis.core.ui.model.imp.XmlGraphicModel` `@XmlRootElement(name = "presentation")` |
| Weasis unit test | `weasis-core/.../imp/suite/SerializationTest.java` marshals `<presentation>…</presentation>` |
| This repo | `scripts/run-xml-graphics-probe.sh` → `corpus/goldens/G-P0-017.json` |

`hasSerializableGraphics()` skips empty models and non-serializable layers; export still goes through JAXB marshal of `XmlGraphicModel`.

**Probe run:** `scripts/run-xml-graphics-probe.sh` builds a **non-empty** `XmlGraphicModel` (`PointGraphic` on `DRAW`) and calls `XmlSerializer.writePresentation(GraphicModel, Writer)`. `hasSerializableGraphics` and `fourSevenWritesXmlGraphics` are **true**. `O-P5-008` applies.
