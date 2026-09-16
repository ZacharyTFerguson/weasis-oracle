# Console `help` (G-P0-014)

## Default GUI binary

`Weasis.cfg` ships `-Dgosh.port=17179`. `conf/base.json` auto-starts `gogo.runtime` and `gogo.command` but **not** `org.apache.felix.gogo.shell`. `WeasisLauncher.executeCommands` starts `telnetd` only if that bundle is already `ACTIVE`. On the frozen 4.7 Linux amd64 installer JVM, and on AppLauncher with default `base.json`, port 17179 **never listened**.

## Live help (shipped overlay)

The installer also ships `conf/base-shell.json`, which auto-starts `gogo.command-1.1.2` and `gogo.shell-1.1.4`. Launching the **same 4.7 bundles** with:

```
-Dfelix.extended.config.properties=file:conf/base-shell.json -Dgosh.port=17179
```

binds `telnetd` on `127.0.0.1:17179`. `felix:lb` showed gogo.runtime 1.1.6, gogo.command 1.1.2, gogo.shell 1.1.4 **ACTIVE**. `weasis:info -a` printed **Weasis 4.7.0**.

Full transcript: [gogo-help-live.txt](gogo-help-live.txt)

Commands from live `help`: `dicom:get` / `dicom:rs` / `dicom:close`, `weasis:ui` / `weasis:info`, `image:get` / `image:close`, `dcmview2d:*` (layout, mouseLeftAction, move, reset, scroll, synch, wl, zoom), plus Felix/Gogo/CM/SCR/OBR.

`cdb-ext` does **not** appear. Flag text from `dicom:get -?` / `dicom:rs -?` / `dicom:close -?` matches [command-grammar.md](../command-grammar.md) (`-p --patient` is listed in `dicom:close -?` even though that command’s Usage line omits it).

Do not tick `G-P0-014` without `G-P0-019`.
