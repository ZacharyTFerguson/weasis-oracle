import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.instrument.Instrumentation;
import java.lang.management.ManagementFactory;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import javax.management.MBeanServer;
import javax.management.ObjectName;

/**
 * Loaded into the running 4.7 Weasis JVM (G-P0-000 / G-P0-014). Uses the MainWindow
 * classloader so OSGi types resolve. Does not reimplement applySplittingRules.
 *
 * <p>{@code jcmd <pid> JVMTI.agent_load FelixLiveDump.jar /path/out.json}
 */
public final class FelixLiveDump {
  public static void agentmain(String args, Instrumentation inst) {
    dump(args);
  }

  public static void premain(String args, Instrumentation inst) {
    dump(args);
  }

  private static void dump(String args) {
    Path out =
        Path.of(
            args == null || args.isBlank()
                ? "/tmp/felix-live-dump.json"
                : args.trim().split("\\s+")[0]);
    StringBuilder json = new StringBuilder();
    json.append("{\n");
    json.append("  \"schemaVersion\": \"genesis.oracle.v1\",\n");
    json.append("  \"caseId\": \"G-P0-000\",\n");
    json.append("  \"class\": \"ST\",\n");
    json.append("  \"producer\": \"felix-live-attach\",\n");
    json.append("  \"weasisVersion\": \"4.7.0\",\n");
    json.append("  \"weasisCommit\": \"3b3e46c59879ead782e5c474e895befae616a715\",\n");
    json.append("  \"pid\": ").append(ProcessHandle.current().pid()).append(",\n");
    try {
      MBeanServer server = ManagementFactory.getPlatformMBeanServer();
      ObjectName name = new ObjectName("weasis:name=MainWindow");
      Object root = server.getAttribute(name, "RootPaneContainer");
      Object config = server.getAttribute(name, "ConfigData");
      ClassLoader cl = resolveWeasisLoader(root);
      json.append("  \"mainWindowClass\": ")
          .append(esc(root.getClass().getName()))
          .append(",\n");
      json.append("  \"classLoader\": ")
          .append(esc(cl == null ? "null" : cl.getClass().getName() + ":" + cl))
          .append(",\n");
      json.append("  \"configData\": ").append(configJson(config)).append(",\n");
      if (cl == null) {
        json.append("  \"error\": \"no Weasis classloader\"\n");
        throw new IllegalStateException("no Weasis classloader");
      }

      Class<?> guiUtils = cl.loadClass("org.weasis.core.api.gui.util.GuiUtils");
      Object ui = guiUtils.getMethod("getUICore").invoke(null);
      json.append("  \"uiCoreClass\": ").append(esc(ui.getClass().getName())).append(",\n");
      json.append("  \"systemPreferences\": ")
          .append(propsJson(invoke(ui, "getSystemPreferences")))
          .append(",\n");
      json.append("  \"localPersistence\": ")
          .append(propsJson(invoke(ui, "getLocalPersistence")))
          .append(",\n");
      json.append("  \"hangingProtocols\": ").append(hangingJson(explorerLoader(ui))).append(",\n");
      json.append("  \"explorers\": ").append(explorersJson(ui, cl)).append(",\n");
      json.append("  \"hiddenSeriesManager\": ").append(hiddenJson(explorerLoader(ui))).append(",\n");
      json.append("  \"applySplittingRules\": ").append(applySplitJson(ui, explorerLoader(ui))).append(",\n");
      json.append("  \"uidIngest\": ").append(uidIngestJson(ui, explorerLoader(ui))).append(",\n");
      json.append("  \"localPropertyProjection\": ").append(propertyProjection(ui)).append(",\n");
      json.append("  \"gogoHelp\": ").append(gogoHelpJson(cl, guiUtils)).append("\n");
    } catch (Throwable t) {
      json.append("  \"error\": ").append(esc(stack(t))).append("\n");
    }
    json.append("}\n");
    try {
      if (out.getParent() != null) {
        Files.createDirectories(out.getParent());
      }
      Files.writeString(out, json.toString(), StandardCharsets.UTF_8);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

  private static ClassLoader resolveWeasisLoader(Object root) {
    try {
      if (root instanceof java.awt.Component c) {
        ClassLoader found = scanComponent(c, 0);
        if (found != null) {
          return found;
        }
      }
    } catch (Throwable ignored) {
    }
    for (java.awt.Window w : java.awt.Window.getWindows()) {
      ClassLoader found = scanComponent(w, 0);
      if (found != null) {
        return found;
      }
    }
    for (Thread t : Thread.getAllStackTraces().keySet()) {
      ClassLoader tcl = t.getContextClassLoader();
      if (tcl == null) {
        continue;
      }
      try {
        tcl.loadClass("org.weasis.core.api.gui.util.GuiUtils");
        return tcl;
      } catch (Throwable ignored) {
      }
    }
    return null;
  }

  private static ClassLoader scanComponent(java.awt.Component c, int depth) {
    if (c == null || depth > 12) {
      return null;
    }
    ClassLoader cl = c.getClass().getClassLoader();
    if (cl != null && c.getClass().getName().startsWith("org.weasis.")) {
      return cl;
    }
    if (c instanceof java.awt.Container box) {
      for (java.awt.Component kid : box.getComponents()) {
        ClassLoader found = scanComponent(kid, depth + 1);
        if (found != null) {
          return found;
        }
      }
    }
    return cl != null && looksLikeWeasis(cl) ? cl : null;
  }

  private static ClassLoader explorerLoader(Object ui) {
    try {
      Collection<?> explorers = (Collection<?>) invoke(ui, "getExplorerPlugins");
      for (Object ex : explorers) {
        ClassLoader cl = ex.getClass().getClassLoader();
        if (cl != null) {
          return cl;
        }
      }
    } catch (Throwable ignored) {
    }
    return ui.getClass().getClassLoader();
  }

  private static boolean looksLikeWeasis(ClassLoader cl) {
    try {
      cl.loadClass("org.weasis.core.api.gui.util.GuiUtils");
      return true;
    } catch (Throwable t) {
      return false;
    }
  }

  private static String hangingJson(ClassLoader cl) {
    try {
      Class<?> hp = cl.loadClass("org.weasis.dicom.explorer.HangingProtocols");
      boolean closePrev = (Boolean) hp.getMethod("isClosePreviousFromPreferences").invoke(null);
      Object[] modes = hp.getDeclaredClasses()[0].getEnumConstants();
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      b.append("    \"engine\": \"OpeningViewer enum + weasis.open.viewer.clean\",\n");
      b.append("    \"closePreviousFromPreferences\": ").append(closePrev).append(",\n");
      b.append("    \"openingViewerModes\": [");
      for (int i = 0; i < modes.length; i++) {
        if (i > 0) {
          b.append(", ");
        }
        b.append(esc(String.valueOf(modes[i])));
      }
      b.append("]\n");
      b.append("  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static String explorersJson(Object ui, ClassLoader cl) {
    try {
      Collection<?> explorers = (Collection<?>) invoke(ui, "getExplorerPlugins");
      StringBuilder b = new StringBuilder();
      b.append("[\n");
      int i = 0;
      for (Object ex : explorers) {
        if (i++ > 0) {
          b.append(",\n");
        }
        b.append("    {\n");
        b.append("      \"class\": ").append(esc(ex.getClass().getName())).append(",\n");
        Object uiName = tryInvoke(ex, "getUIName");
        if (uiName != null) {
          b.append("      \"uiName\": ").append(esc(String.valueOf(uiName))).append(",\n");
        }
        Object model = tryInvoke(ex, "getDataExplorerModel");
        b.append("      \"modelClass\": ")
            .append(esc(model == null ? "null" : model.getClass().getName()))
            .append(",\n");
        b.append("      \"tree\": ").append(treeJson(model, cl)).append("\n");
        b.append("    }");
      }
      b.append("\n  ]");
      return b.toString();
    } catch (Throwable t) {
      return arrError(stack(t));
    }
  }

  private static String treeJson(Object model, ClassLoader cl) {
    if (model == null) {
      return "null";
    }
    try {
      Class<?> nodeCl = cl.loadClass("org.weasis.core.api.media.data.MediaSeriesGroupNode");
      Object root = nodeCl.getField("rootNode").get(null);
      return nodeJson(model, root, 0);
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static String nodeJson(Object model, Object node, int depth) {
    if (depth > 8 || node == null) {
      return "null";
    }
    StringBuilder b = new StringBuilder();
    b.append("{\n");
    indent(b, depth + 8);
    b.append("\"toString\": ").append(esc(String.valueOf(node))).append(",\n");
    indent(b, depth + 8);
    b.append("\"class\": ").append(esc(node.getClass().getName())).append(",\n");
    Object mime = tryInvoke(node, "getMimeType");
    if (mime != null) {
      indent(b, depth + 8);
      b.append("\"mimeType\": ").append(esc(String.valueOf(mime))).append(",\n");
    }
    Object size = tryInvoke(node, "size", new Class<?>[] {Object.class}, new Object[] {null});
    if (size instanceof Number) {
      indent(b, depth + 8);
      b.append("\"size\": ").append(size).append(",\n");
    }
    Collection<?> kids = null;
    try {
      kids = (Collection<?>) model.getClass().getMethod("getChildren", node.getClass().getInterfaces()[0])
          .invoke(model, node);
    } catch (Throwable ignored) {
      try {
        for (Method m : model.getClass().getMethods()) {
          if ("getChildren".equals(m.getName()) && m.getParameterCount() == 1) {
            kids = (Collection<?>) m.invoke(model, node);
            break;
          }
        }
      } catch (Throwable t) {
        indent(b, depth + 8);
        b.append("\"childrenError\": ").append(esc(stack(t))).append("\n");
        indent(b, depth + 6);
        b.append("}");
        return b.toString();
      }
    }
    indent(b, depth + 8);
    b.append("\"children\": [");
    if (kids != null && !kids.isEmpty()) {
      b.append("\n");
      int i = 0;
      for (Object kid : kids) {
        if (i++ > 0) {
          b.append(",\n");
        }
        indent(b, depth + 10);
        b.append(nodeJson(model, kid, depth + 1));
      }
      b.append("\n");
      indent(b, depth + 8);
    }
    b.append("]\n");
    indent(b, depth + 6);
    b.append("}");
    return b.toString();
  }

  private static String hiddenJson(ClassLoader cl) {
    try {
      Class<?> hsm = cl.loadClass("org.weasis.dicom.codec.HiddenSeriesManager");
      Object inst = hsm.getMethod("getInstance").invoke(null);
      Map<?, ?> series2 = (Map<?, ?>) hsm.getField("series2Elements").get(inst);
      Map<?, ?> patient2 = (Map<?, ?>) hsm.getField("patient2Series").get(inst);
      Map<?, ?> ref2 = (Map<?, ?>) hsm.getField("reference2Series").get(inst);
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      b.append("    \"series2ElementsCount\": ").append(series2.size()).append(",\n");
      b.append("    \"patient2SeriesCount\": ").append(patient2.size()).append(",\n");
      b.append("    \"reference2SeriesCount\": ").append(ref2.size()).append(",\n");
      b.append("    \"series2Elements\": {\n");
      int i = 0;
      for (Map.Entry<?, ?> e : series2.entrySet()) {
        if (i++ > 0) {
          b.append(",\n");
        }
        b.append("      ").append(esc(String.valueOf(e.getKey()))).append(": [");
        Object val = e.getValue();
        if (val instanceof Collection<?> c) {
          int j = 0;
          for (Object el : c) {
            if (j++ > 0) {
              b.append(", ");
            }
            b.append(esc(el.getClass().getSimpleName() + ":" + el));
          }
        }
        b.append("]");
      }
      b.append("\n    }\n  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static String gogoHelpJson(ClassLoader cl, Class<?> weasisWinClass) {
    try {
      Class<?> appProps = cl.loadClass("org.weasis.core.api.gui.util.AppProperties");
      Object ctx = appProps.getMethod("getBundleContext", Class.class).invoke(null, weasisWinClass);
      if (ctx == null) {
        ctx = appProps.getMethod("getBundleContext").invoke(null);
      }
      Method refsMethod =
          ctx.getClass().getMethod("getServiceReferences", String.class, String.class);
      refsMethod.setAccessible(true);
      Object refs = refsMethod.invoke(ctx, "org.apache.felix.service.command.CommandProcessor", null);
      if (refs == null) {
        return obj("status", "no CommandProcessor references");
      }
      Object[] arr;
      if (refs instanceof Object[] a) {
        arr = a;
      } else if (refs instanceof Collection<?> c) {
        arr = c.toArray();
      } else {
        return obj("status", "unexpected refs type " + refs.getClass().getName());
      }
      if (arr.length == 0) {
        return obj("status", "empty CommandProcessor references");
      }
      Object processor = null;
      for (Method m : ctx.getClass().getMethods()) {
        if ("getService".equals(m.getName()) && m.getParameterCount() == 1) {
          m.setAccessible(true);
          try {
            processor = m.invoke(ctx, arr[0]);
          } catch (Throwable ignored) {
            continue;
          }
          if (processor != null) {
            break;
          }
        }
      }
      ByteArrayOutputStream bout = new ByteArrayOutputStream();
      ByteArrayOutputStream berr = new ByteArrayOutputStream();
      Object session =
          processor
              .getClass()
              .getMethod(
                  "createSession",
                  java.io.InputStream.class,
                  PrintStream.class,
                  PrintStream.class)
              .invoke(
                  processor,
                  new ByteArrayInputStream(new byte[0]),
                  new PrintStream(bout, true, StandardCharsets.UTF_8),
                  new PrintStream(berr, true, StandardCharsets.UTF_8));
      Object result = session.getClass().getMethod("execute", CharSequence.class).invoke(session, "help");
      try {
        session.getClass().getMethod("close").invoke(session);
      } catch (Throwable ignored) {
      }
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      b.append("    \"status\": \"executed\",\n");
      b.append("    \"stdout\": ").append(esc(bout.toString(StandardCharsets.UTF_8))).append(",\n");
      b.append("    \"stderr\": ").append(esc(berr.toString(StandardCharsets.UTF_8))).append(",\n");
      b.append("    \"result\": ").append(esc(String.valueOf(result))).append("\n");
      b.append("  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static String configJson(Object config) {
    if (config == null) {
      return "null";
    }
    StringBuilder b = new StringBuilder();
    b.append("{\n");
    b.append("    \"class\": ").append(esc(config.getClass().getName())).append(",\n");
    Object props = tryInvoke(config, "getProperties");
    if (props instanceof Properties p) {
      b.append("    \"properties\": ").append(javaPropsJson(p)).append("\n");
    } else if (props instanceof Map<?, ?> m) {
      b.append("    \"properties\": ").append(mapJson(m)).append("\n");
    } else {
      b.append("    \"toString\": ").append(esc(String.valueOf(config))).append("\n");
    }
    b.append("  }");
    return b.toString();
  }

  private static String propsJson(Object props) {
    if (props == null) {
      return "null";
    }
    if (props instanceof Properties p) {
      return javaPropsJson(p);
    }
    Object inner = tryInvoke(props, "getProperties");
    if (inner instanceof Properties p) {
      return javaPropsJson(p);
    }
    if (props instanceof Map<?, ?> m) {
      return mapJson(m);
    }
    try {
      Method keys = props.getClass().getMethod("stringPropertyNames");
      Set<?> names = (Set<?>) keys.invoke(props);
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      int i = 0;
      for (Object k : names) {
        if (i++ > 0) {
          b.append(",\n");
        }
        Object v = props.getClass().getMethod("getProperty", String.class).invoke(props, String.valueOf(k));
        b.append("    ").append(esc(String.valueOf(k))).append(": ").append(esc(String.valueOf(v)));
      }
      b.append("\n  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("toString", String.valueOf(props));
    }
  }

  private static String javaPropsJson(Properties p) {
    StringBuilder b = new StringBuilder();
    b.append("{\n");
    int i = 0;
    for (String k : p.stringPropertyNames()) {
      if (i++ > 0) {
        b.append(",\n");
      }
      b.append("    ").append(esc(k)).append(": ").append(esc(p.getProperty(k)));
    }
    b.append("\n  }");
    return b.toString();
  }

  private static String mapJson(Map<?, ?> m) {
    StringBuilder b = new StringBuilder();
    b.append("{\n");
    int i = 0;
    for (Map.Entry<?, ?> e : m.entrySet()) {
      if (i++ > 0) {
        b.append(",\n");
      }
      b.append("    ").append(esc(String.valueOf(e.getKey()))).append(": ").append(esc(String.valueOf(e.getValue())));
    }
    b.append("\n  }");
    return b.toString();
  }

  private static String applySplitJson(Object ui, ClassLoader cl) {
    try {
      Class<?> tagD = cl.loadClass("org.weasis.dicom.codec.TagD");
      Class<?> tagW = cl.loadClass("org.weasis.core.api.media.data.TagW");
      Class<?> levelCl = cl.loadClass("org.weasis.dicom.codec.TagD$Level");
      Object studyLevel = Enum.valueOf(levelCl.asSubclass(Enum.class), "STUDY");
      Object instanceLevel = Enum.valueOf(levelCl.asSubclass(Enum.class), "INSTANCE");
      Method tagGet = tagD.getMethod("get", int.class);
      Method tagGetUID = tagD.getMethod("getUID", levelCl);
      Object seriesUidTag = tagGet.invoke(null, 0x0020000E);
      Object studyUidTag = tagGetUID.invoke(null, studyLevel);
      Object sopUidTag = tagGetUID.invoke(null, instanceLevel);
      Object kernelTag = tagGet.invoke(null, 0x00181210);
      Object iopTag = tagGet.invoke(null, 0x00200037);
      Object splitTag = tagW.getField("SplitSeriesNumber").get(null);
      Collection<?> explorers = (Collection<?>) invoke(ui, "getExplorerPlugins");
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      b.append("    \"api\": \"org.weasis.dicom.explorer.DicomModel.applySplittingRules\",\n");
      b.append("    \"invokedBy\": \"LoadDicom.getDicomImageElements\",\n");
      b.append("    \"note\": \"groups and order from live DicomModel after LoadDicom, not SeriesSplitHarness\",\n");
      b.append("    \"series\": [\n");
      int si = 0;
      for (Object ex : explorers) {
        Object model = tryInvoke(ex, "getDataExplorerModel");
        if (model == null) {
          continue;
        }
        Class<?> nodeCl = cl.loadClass("org.weasis.core.api.media.data.MediaSeriesGroupNode");
        Object root = nodeCl.getField("rootNode").get(null);
        si = walkSeries(b, model, root, 0, si, seriesUidTag, studyUidTag, sopUidTag, kernelTag, iopTag, splitTag);
      }
      b.append("\n    ]\n  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static int walkSeries(
      StringBuilder b,
      Object model,
      Object node,
      int depth,
      int si,
      Object seriesUidTag,
      Object studyUidTag,
      Object sopUidTag,
      Object kernelTag,
      Object iopTag,
      Object splitTag) {
    if (node == null || depth > 8) {
      return si;
    }
    String cls = node.getClass().getName();
    if (cls.contains("DicomSeries") || "series/dicom".equals(String.valueOf(tryInvoke(node, "getMimeType")))) {
      if (si++ > 0) {
        b.append(",\n");
      }
      b.append("      {\n");
      b.append("        \"toString\": ").append(esc(String.valueOf(node))).append(",\n");
      b.append("        \"class\": ").append(esc(cls)).append(",\n");
      b.append("        \"studyInstanceUID\": ").append(esc(stringifyTag(node, studyUidTag))).append(",\n");
      b.append("        \"seriesInstanceUID\": ").append(esc(stringifyTag(node, seriesUidTag))).append(",\n");
      b.append("        \"convolutionKernel\": ").append(esc(stringifyTag(node, kernelTag))).append(",\n");
      b.append("        \"imageOrientationPatient\": ").append(esc(stringifyTag(node, iopTag))).append(",\n");
      b.append("        \"splitSeriesNumber\": ").append(esc(stringifyTag(node, splitTag))).append(",\n");
      b.append("        \"medias\": [");
      int mi = 0;
      try {
        Method getMedias = null;
        for (Method m : node.getClass().getMethods()) {
          if ("getMedias".equals(m.getName()) && m.getParameterCount() == 2) {
            getMedias = m;
            break;
          }
        }
        if (getMedias != null) {
          Object it = getMedias.invoke(node, null, null);
          if (it instanceof Iterable<?> medias) {
            for (Object media : medias) {
              if (mi++ > 0) {
                b.append(", ");
              }
              b.append(esc(stringifyTag(media, sopUidTag)));
            }
          }
        }
      } catch (Throwable ignored) {
      }
      b.append("]\n      }");
    }
    Collection<?> kids = childrenOf(model, node);
    if (kids != null) {
      for (Object kid : kids) {
        si = walkSeries(b, model, kid, depth + 1, si, seriesUidTag, studyUidTag, sopUidTag, kernelTag, iopTag, splitTag);
      }
    }
    return si;
  }

  private static String uidIngestJson(Object ui, ClassLoader cl) {
    try {
      Class<?> tagD = cl.loadClass("org.weasis.dicom.codec.TagD");
      Class<?> levelCl = cl.loadClass("org.weasis.dicom.codec.TagD$Level");
      Object studyLevel = Enum.valueOf(levelCl.asSubclass(Enum.class), "STUDY");
      Object instanceLevel = Enum.valueOf(levelCl.asSubclass(Enum.class), "INSTANCE");
      Method tagGet = tagD.getMethod("get", int.class);
      Method tagGetUID = tagD.getMethod("getUID", levelCl);
      Object seriesUidTag = tagGet.invoke(null, 0x0020000E);
      Object studyUidTag = tagGetUID.invoke(null, studyLevel);
      Object sopUidTag = tagGetUID.invoke(null, instanceLevel);
      StringBuilder b = new StringBuilder();
      b.append("{\n");
      b.append("    \"ingestSite\": \"LoadDicom.buildDicomStructure + DicomMediaIO.writeInstanceTags\",\n");
      b.append("    \"createUIDAtIngest\": false,\n");
      b.append("    \"nodes\": [\n");
      int n = 0;
      Collection<?> explorers = (Collection<?>) invoke(ui, "getExplorerPlugins");
      for (Object ex : explorers) {
        Object model = tryInvoke(ex, "getDataExplorerModel");
        if (model == null) {
          continue;
        }
        Class<?> nodeCl = cl.loadClass("org.weasis.core.api.media.data.MediaSeriesGroupNode");
        Object root = nodeCl.getField("rootNode").get(null);
        n = walkUidNodes(b, model, root, 0, n, studyUidTag, seriesUidTag, sopUidTag);
      }
      b.append("\n    ]\n  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static int walkUidNodes(
      StringBuilder b,
      Object model,
      Object node,
      int depth,
      int n,
      Object studyUidTag,
      Object seriesUidTag,
      Object sopUidTag) {
    if (node == null || depth > 8) {
      return n;
    }
    String cls = node.getClass().getName();
    if (cls.contains("MediaSeriesGroup") || cls.contains("DicomSeries") || cls.contains("GroupNode")) {
      String study = stringifyTag(node, studyUidTag);
      String series = stringifyTag(node, seriesUidTag);
      if (study != null || series != null) {
        if (n++ > 0) {
          b.append(",\n");
        }
        b.append("      {\"class\": ")
            .append(esc(cls))
            .append(", \"toString\": ")
            .append(esc(String.valueOf(node)))
            .append(", \"studyInstanceUID\": ")
            .append(esc(study))
            .append(", \"seriesInstanceUID\": ")
            .append(esc(series))
            .append(", \"sopInstanceUID\": ")
            .append(esc(stringifyTag(node, sopUidTag)))
            .append("}");
      }
    }
    Collection<?> kids = childrenOf(model, node);
    if (kids != null) {
      for (Object kid : kids) {
        n = walkUidNodes(b, model, kid, depth + 1, n, studyUidTag, seriesUidTag, sopUidTag);
      }
    }
    return n;
  }

  private static String propertyProjection(Object ui) {
    try {
      Object sys = invoke(ui, "getSystemPreferences");
      Object local = invoke(ui, "getLocalPersistence");
      String[] keys = {
        "locale.lang.code",
        "locale.format.code",
        "weasis.download.immediately",
        "explorer.thumbnail.size",
        "weasis.theme",
        "weasis.version",
        "weasis.update.release"
      };
      StringBuilder b = new StringBuilder("{\n");
      b.append("    \"source\": \"UICore.getSystemPreferences + getLocalPersistence\",\n");
      b.append("    \"pidFree\": true,\n");
      b.append("    \"keys\": {\n");
      for (int i = 0; i < keys.length; i++) {
        String v = prefGet(sys, keys[i]);
        if (v == null) {
          v = prefGet(local, keys[i]);
        }
        if (i > 0) {
          b.append(",\n");
        }
        b.append("      ").append(esc(keys[i])).append(": ").append(esc(v));
      }
      b.append("\n    }\n  }");
      return b.toString();
    } catch (Throwable t) {
      return obj("error", stack(t));
    }
  }

  private static String prefGet(Object props, String key) {
    if (props == null) {
      return null;
    }
    try {
      Object v = props.getClass().getMethod("getProperty", String.class).invoke(props, key);
      return v == null ? null : String.valueOf(v);
    } catch (Throwable t) {
      return null;
    }
  }

  private static Collection<?> childrenOf(Object model, Object node) {
    try {
      for (Method m : model.getClass().getMethods()) {
        if ("getChildren".equals(m.getName()) && m.getParameterCount() == 1) {
          Object kids = m.invoke(model, node);
          if (kids instanceof Collection<?> c) {
            return c;
          }
        }
      }
    } catch (Throwable ignored) {
    }
    return null;
  }

  private static String stringifyTag(Object target, Object tag) {
    if (target == null || tag == null) {
      return null;
    }
    try {
      for (Method m : target.getClass().getMethods()) {
        if ("getTagValue".equals(m.getName()) && m.getParameterCount() == 1) {
          Object v = m.invoke(target, tag);
          if (v == null) {
            return null;
          }
          if (v instanceof Object[] arr) {
            StringBuilder b = new StringBuilder();
            for (int i = 0; i < arr.length; i++) {
              if (i > 0) {
                b.append('\\');
              }
              b.append(arr[i]);
            }
            return b.toString();
          }
          return String.valueOf(v);
        }
      }
    } catch (Throwable ignored) {
    }
    return null;
  }

  private static Object invoke(Object target, String method) throws Exception {
    return target.getClass().getMethod(method).invoke(target);
  }

  private static Object tryInvoke(Object target, String method) {
    try {
      return target.getClass().getMethod(method).invoke(target);
    } catch (Throwable t) {
      return null;
    }
  }

  private static Object tryInvoke(Object target, String method, Class<?>[] types, Object[] args) {
    try {
      return target.getClass().getMethod(method, types).invoke(target, args);
    } catch (Throwable t) {
      return null;
    }
  }

  private static void indent(StringBuilder b, int n) {
    b.append(" ".repeat(Math.max(0, n)));
  }

  private static String obj(String k, String v) {
    return "{ \"" + k + "\": " + esc(v) + " }";
  }

  private static String arrError(String v) {
    return "[ { \"error\": " + esc(v) + " } ]";
  }

  private static String stack(Throwable t) {
    StringWriter sw = new StringWriter();
    t.printStackTrace(new PrintWriter(sw));
    return sw.toString();
  }

  private static String esc(String s) {
    if (s == null) {
      return "null";
    }
    StringBuilder b = new StringBuilder("\"");
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      switch (c) {
        case '"' -> b.append("\\\"");
        case '\\' -> b.append("\\\\");
        case '\n' -> b.append("\\n");
        case '\r' -> b.append("\\r");
        case '\t' -> b.append("\\t");
        default -> {
          if (c < 32) {
            b.append(String.format("\\u%04x", (int) c));
          } else {
            b.append(c);
          }
        }
      }
    }
    b.append('"');
    return b.toString();
  }
}
