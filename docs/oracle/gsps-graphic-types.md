# GSPS graphic types Weasis 4.7 renders

From `org.weasis.dicom.explorer.pr.PrGraphicUtil.getGraphicBuilder` on SHA `3b3e46c59879ead782e5c474e895befae616a715`.

## Rendered (builder exists)

| Type | Sequence | Builder |
| --- | --- | --- |
| POINT | GraphicObject | `buildPoint` |
| POLYLINE | GraphicObject | `buildPolyline` |
| MULTILINE | CompoundGraphic | `buildPolyline` |
| INTERPOLATED | GraphicObject | `buildInterpolated` |
| CIRCLE | GraphicObject | `buildCircle` |
| ELLIPSE | GraphicObject | `buildEllipse` |
| MULTIPOINT | CompoundGraphic | `buildMultiPoint` |
| RECTANGLE | CompoundGraphic | `buildRectangle` |
| RULER | CompoundGraphic | `buildLine` |
| ARROW | CompoundGraphic | `buildLine` |

## Not rendered (`default -> null`)

INFINITELINE, CUTLINE, RANGELINE, AXIS, CROSSHAIR.

## Corpus

`corpus/phantoms/G-P0-iod-pr-gsps-types.dcm` carries one GraphicObject or CompoundGraphic of each **rendered** type. §0.8 GSPS-every-type cell follows this list, not the full DICOM compound-type enum.
