# 3D Viewer census from frozen 4.7 bytecode (G-P0-014)

This VM has **no usable OpenGL**. Live GUI is the shipped **Opengl Error** dialog (`208-3d-viewer.png`, prefs `36-prefs-3dviewer.png`), not a 4.7 feature absence. Do **not** tick `G-P0-014` / `G-P0-019` from this file.

Bundle: `weasis-dicom-viewer3d-4.7.0.jar` (installer `bundle/weasis-dicom-viewer3d-4.7.0.jar.xz`).

## Factory

`org.weasis.dicom.viewer3d.View3DFactory` implements `SeriesViewerFactory`.

- `NAME` / `getUIName` → **3D Viewer** (live dump `uiName=3D Viewer`, `level=10`, `video/dicom=false`)
- Pref keys: `P_DEFAULT_LAYOUT`, `P_OPENGL_ENABLE`, `P_OPENGL_PREV_INIT`, `P_FORCE_FBO`
- `isOpenglEnable()`, `getOpenGLInfo()`, `showOpenglErrorMessage(Component)` — live path for `208`
- Error strings from [viewer3d-messages.properties](viewer3d-messages.properties): `opengl.error=Opengl Error`, `opengl.error.msg=Volume Rendering requires OpenGL capabilities`, `check.in.preferences=Check in preferences`, `no.graphic.card=No graphic card found or required OpenGL capabilities not available`

OSGi components: `View3DFactory`, `ExternalView3DBarFactory`, `Viewer3dPrefFactory`, `SegmentationToolFactory`.

## Chrome that exists when OpenGL works (`ActionVol`)

| Feature | Kind |
| --- | --- |
| `SCROLLING` | slider |
| `VOL_PRESET` | combo (`vr.Preset`) |
| `VOL_AXIS` | combo (`geometry.Axis`) |
| `VOL_QUALITY` | slider |
| `VOL_SHADING` | toggle |
| `VOL_PROJECTION` | toggle |
| `RENDERING_TYPE` | combo (`vr.RenderingType`) |
| `VOL_OPACITY` | slider |
| `ORIENTATION_CUBE` | action |
| `SEG_TYPE` | combo (`SegmentationTool.Type`) |
| `MPR_CROSSHAIR` | action |
| `CROSSHAIR_CUT_MODE` | combo (`vr.CrosshairCutMode`) |

UI strings for those (same properties file): Volume rendering, Orientation cube, Orthographic Projection, Z-axis sampling, Shading, Slicing, Composite, Isosurface, MIP (Max) / MinIP (Min) / AIP (Mean), Volume LUT Bar, Rebuild the volume, 3D Settings, MPR Crosshair Cut (No cut / Left / Right / Up / Down / Front / Back / 1/4 / 1/8 cuts), Segmentation none / only / overlay.

Prefs page (`Viewer3dPrefView`): OpenGL Support, Enable, Graphic card, Driver version, Max 3D texture dimension length, Default layout, Dynamic quality, Hardware acceleration warning.

## 4.7 rejects software OpenGL (this VM cannot grow a volume tab)

Frozen `OpenGLInfo.looksSoftware()` is true when the renderer name contains `llvmpipe`, `softpipe`, `swiftshader`, or ANGLE+WARP. `View3DFactory.initOpenGLInfo` then throws:

`The OpenGL renderer seems to be a software renderer without real GPU`

and writes `opengl.enable=false`. Mesa llvmpipe on this cloud VM is therefore **not** a way to screenshot `ActionVol` chrome. Live 4.7 path here stays `208` / prefs `36`. That is 4.7 design, not an unfinished census page.

Live JVMTI dump on this AppLauncher (`CensusGlAj014`, [gl-info-aj014.txt](gl-info-aj014.txt)): persistence started `opengl.enable=false` / `opengl.prev.init=false` so `GraphicsInfo` was empty. Forcing `getOpenGLInfo()` after `opengl.enable=true` returned:

`renderer=llvmpipe (LLVM 20.1.2, 256 bits)` `vendor=Mesa` `shortVersion=4.5 (Core Profile) Mesa 25.2.8-0ubuntu0.24.04.1` `max3dTextureSize=2048` **`looksSoftware=true`**

OpenGL **4.5** is above the 3.3 floor; the reject is the software-renderer check, not a missing GPU API. After the throw, 4.7 wrote `opengl.enable=false` again. `GraphicsInfo` then `Gpu[..., softwareRendered=true]`. Prefs `36` shows **No graphic card found** because `getOpenGLInfo()` is skipped once enable is false — not because Mesa was never probed.

`weasis.force.3d` only forces the enable flags; `getOpenGLInfo()` still rejects software renderers.

Classes that would host the volume tab: `View3DContainer`, `View3d` / `VolumeCanvas`, `View3DToolbar`, `VolLutToolBar`, `ExternalView3DToolbar`, `InfoLayer3d`.

Live on this VM: toolbar **Open the series in the 3D viewer** → modal Opengl Error → **Check in preferences** / **OK**. No `View3DContainer` tab.
