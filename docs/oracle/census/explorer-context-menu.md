# Explorer and tab context menus (G-P0-014, unsigned)

Do **not** tick `G-P0-014`. Classes: frozen v4.7.0 `ThumbnailMouseAndKeyAdapter.showContextMenu` (`weasis-dicom-explorer-4.7.0`) and Docking Frames tab actions on `ViewerPlugin`. SHA `3b3e46c59879ead782e5c474e895befae616a715`. Live popups from BUTTON3 inside the running AppLauncher.

## Live GUI (this session)

| Shot | What |
| --- | --- |
| `182-explorer-context.png` | Series thumbnail popup: **2D Viewer ▸**, Select related Series, Select related Series (same axis), Remove selected Series / this Study / this Patient |
| `183-explorer-2dviewer-flyout.png` | **2D Viewer** flyout: Open, Open in new tab, Add |
| `184-tab-context.png` | Viewer tab `GENESIS, PHANTOM`: Close Others, Close All, Maximize `Ctrl+M`, Close `Ctrl+W` |

Not shown on this one-series / one-screen phantom (code still has them): Open in screen (needs `GraphicsDevice.length > 1`), Merge selected Series (needs more than one series), Stop All / Resume All (`LoadSeries`), Rebuild Thumbnail, Open Key Images (needs KO), Open DICOM information (`MimeSystemAppFactory`).

## Class order (`showContextMenu`)

1. Per viewer factory submenu (`getUIName()`, here **2D Viewer**): Open; Open in new tab when `canExternalizeSeries`; Open in screen when more than one `GraphicsDevice`; Add when `canAddSeries`; Open DICOM information when `MimeSystemAppFactory`
2. If exactly one series: Select related Series; Select related Series (same axis)
3. Load-series Stop All / Resume All when a `LoadSeries` is attached
4. Merge selected Series when more than one series is selected
5. Remove selected Series / this Study / this Patient
6. Rebuild Thumbnail (from first / middle / last)
7. Open Key Images when a KO special element is attached

## Viewer tab

Live items match `ViewerPlugin.CloseOthersAction` plus the Eclipse-theme docking tab menu: Close Others, Close All, Maximize (`ShortcutManager.dock_maximize` `Ctrl+M`), Close (`Ctrl+W`). Help → Shortcuts text: Open contextual menu (Close Others, All, Maximize).
