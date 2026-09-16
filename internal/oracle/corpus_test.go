package oracle

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestSplitGolden_convolutionKernelGroups(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-000-split.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		Producer string     `json:"producer"`
		Engine   string     `json:"splitEngine"`
		Role     string     `json:"role"`
		Groups   [][]string `json:"groups"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.Producer != "weasis-library-splitting-rules" {
		t.Fatalf("producer %q", g.Producer)
	}
	if g.Engine != "org.weasis.dicom.codec.utils.SplittingRules" {
		t.Fatalf("engine %q", g.Engine)
	}
	if g.Role != "predicate-snapshot-not-grouping-oracle" {
		t.Fatalf("role %q (must not be the grouping oracle)", g.Role)
	}
	if len(g.Groups) != 2 {
		t.Fatalf("want 2 groups (same series, BONE kernel split), got %d: %#v", len(g.Groups), g.Groups)
	}
}

func TestUIDSynthesis_impliedClassST(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-051.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		Class        string `json:"class"`
		UIDSynthesis struct {
			Deterministic         bool   `json:"deterministic"`
			ImpliedClassForOP1011 string `json:"impliedClassForOP1011"`
		} `json:"uidSynthesis"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.UIDSynthesis.Deterministic {
		t.Fatal("UIDUtils.createUID was deterministic; O-P1-011 would stay BE")
	}
	if g.Class != "ST" || g.UIDSynthesis.ImpliedClassForOP1011 != "ST" {
		t.Fatalf("want ST got class=%s implied=%s", g.Class, g.UIDSynthesis.ImpliedClassForOP1011)
	}
}

func TestPin_matchesReferenceJSON(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "docs", "oracle", "reference.json"))
	if err != nil {
		t.Fatal(err)
	}
	var ref Pin
	if err := json.Unmarshal(raw, &ref); err != nil {
		t.Fatal(err)
	}
	if ref != DefaultPin {
		t.Fatalf("reference.json %+v != DefaultPin %+v", ref, DefaultPin)
	}
}

func TestGoldens_schemaVersion(t *testing.T) {
	dir := filepath.Join("..", "..", "corpus", "goldens")
	ents, err := os.ReadDir(dir)
	if err != nil {
		t.Fatal(err)
	}
	n := 0
	for _, e := range ents {
		if e.IsDir() || filepath.Ext(e.Name()) != ".json" {
			continue
		}
		raw, err := os.ReadFile(filepath.Join(dir, e.Name()))
		if err != nil {
			t.Fatal(err)
		}
		var g Golden
		if err := json.Unmarshal(raw, &g); err != nil {
			t.Fatalf("%s: %v", e.Name(), err)
		}
		if g.SchemaVersion != SchemaVersion {
			t.Fatalf("%s schemaVersion %q", e.Name(), g.SchemaVersion)
		}
		if g.CaseID == "" {
			t.Fatalf("%s missing caseId", e.Name())
		}
		n++
	}
	if n < 5 {
		t.Fatalf("too few goldens: %d", n)
	}
}

func TestHTJ2KProbe_fourSevenOpensPixels(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-016.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID             string `json:"caseId"`
		WeasisEnumHasHtj2k bool   `json:"weasisEnumHasHtj2k"`
		Reference          struct {
			OpenCVNativeLoaded bool `json:"opencvNativeLoaded"`
		} `json:"reference"`
		Verdict struct {
			J2KControlOpened             bool `json:"j2kControlOpened"`
			Htj2kObjectsTried            int  `json:"htj2kObjectsTried"`
			Htj2kObjectsOpened           int  `json:"htj2kObjectsOpened"`
			FourSevenOpensHtj2kPixels    bool `json:"fourSevenOpensHtj2kPixels"`
			ExportUIListsHtj2k           bool `json:"exportUiListsHtj2k"`
			ReaderIsSupportedSyntaxHtj2k bool `json:"readerIsSupportedSyntaxHtj2k"`
		} `json:"verdict"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-016" {
		t.Fatalf("caseId %q", g.CaseID)
	}
	if !g.Reference.OpenCVNativeLoaded {
		t.Fatal("opencv native was not loaded; probe is not a 4.7 decode")
	}
	if !g.Verdict.J2KControlOpened {
		t.Fatal("JPEG2000 control did not open; native decode path is broken")
	}
	if g.WeasisEnumHasHtj2k || g.Verdict.ExportUIListsHtj2k || g.Verdict.ReaderIsSupportedSyntaxHtj2k {
		t.Fatal("4.7 started advertising HTJ2K in enum/isSupportedSyntax; re-read G-P0-016")
	}
	if g.Verdict.Htj2kObjectsTried < 3 || g.Verdict.Htj2kObjectsOpened != g.Verdict.Htj2kObjectsTried {
		t.Fatalf("HTJ2K opened %d/%d", g.Verdict.Htj2kObjectsOpened, g.Verdict.Htj2kObjectsTried)
	}
	if !g.Verdict.FourSevenOpensHtj2kPixels {
		t.Fatal("verdict.fourSevenOpensHtj2kPixels is false")
	}
}

func TestXMLGraphics_fourSevenWrites(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-017.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID                     string `json:"caseId"`
		Class                      string `json:"class"`
		XMLContainsPresentation    bool   `json:"xmlContainsPresentation"`
		HasSerializableGraphics    bool   `json:"hasSerializableGraphics"`
		FourSevenWritesXmlGraphics bool   `json:"fourSevenWritesXmlGraphics"`
		OP5008Applies              bool   `json:"oP5008Applies"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-017" {
		t.Fatalf("caseId %q", g.CaseID)
	}
	if g.Class != "ST" {
		t.Fatalf("class %q", g.Class)
	}
	if !g.XMLContainsPresentation || !g.FourSevenWritesXmlGraphics || !g.OP5008Applies {
		t.Fatalf("XML graphics write not proven: %+v", g)
	}
	if !g.HasSerializableGraphics {
		t.Fatal("G-P0-017 must marshal a non-empty hasSerializableGraphics model")
	}
}

func TestSecondOracle_threeWayUncompressedCT(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-052.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID                    string `json:"caseId"`
		ThreeWayStoredPixelsAgree bool   `json:"threeWayStoredPixelsAgree"`
		DcmdumpMatchedListedUIDs  bool   `json:"dcmdumpMatchedListedUIDs"`
		StoredPixelSHA256         struct {
			PydicomPixelData     string `json:"pydicomPixelData"`
			WeasisRawFrame       string `json:"weasisRawFrame"`
			WeasisStoredPixelData string `json:"weasisStoredPixelData"`
		} `json:"storedPixelSHA256"`
		Disagreements []any `json:"disagreements"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-052" {
		t.Fatalf("caseId %q", g.CaseID)
	}
	if !g.ThreeWayStoredPixelsAgree || !g.DcmdumpMatchedListedUIDs || len(g.Disagreements) != 0 {
		t.Fatalf("second oracle not clean: %+v", g)
	}
	weasisStored := g.StoredPixelSHA256.WeasisStoredPixelData
	if weasisStored == "" {
		weasisStored = g.StoredPixelSHA256.WeasisRawFrame
	}
	if g.StoredPixelSHA256.PydicomPixelData == "" || g.StoredPixelSHA256.PydicomPixelData != weasisStored {
		t.Fatalf("stored pixels %+v", g.StoredPixelSHA256)
	}
}

func TestFelixLiveDump_reachability(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-000-felix.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID           string `json:"caseId"`
		Producer         string `json:"producer"`
		HangingProtocols struct {
			Engine             string   `json:"engine"`
			OpeningViewerModes []string `json:"openingViewerModes"`
		} `json:"hangingProtocols"`
		HiddenSeriesManager struct {
			Series2ElementsCount int `json:"series2ElementsCount"`
		} `json:"hiddenSeriesManager"`
		Explorers []struct {
			ModelClass string `json:"modelClass"`
		} `json:"explorers"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-000" || g.Producer != "felix-live-attach" {
		t.Fatalf("case %s producer %s", g.CaseID, g.Producer)
	}
	if len(g.HangingProtocols.OpeningViewerModes) != 2 {
		t.Fatalf("OpeningViewer modes %v", g.HangingProtocols.OpeningViewerModes)
	}
	if g.HiddenSeriesManager.Series2ElementsCount < 3 {
		t.Fatalf("special-element attachments %d", g.HiddenSeriesManager.Series2ElementsCount)
	}
	if len(g.Explorers) == 0 || g.Explorers[0].ModelClass != "org.weasis.dicom.explorer.DicomModel" {
		t.Fatalf("explorers %#v", g.Explorers)
	}
}

func TestFelix_applySplittingRulesDump(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-000-felix.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		ApplySplittingRules struct {
			API    string `json:"api"`
			Series []struct {
				SeriesInstanceUID string   `json:"seriesInstanceUID"`
				Medias            []string `json:"medias"`
			} `json:"series"`
		} `json:"applySplittingRules"`
		LocalPropertyProjection struct {
			PidFree bool `json:"pidFree"`
		} `json:"localPropertyProjection"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.ApplySplittingRules.API != "org.weasis.dicom.explorer.DicomModel.applySplittingRules" {
		t.Fatalf("applySplittingRules.api %q", g.ApplySplittingRules.API)
	}
	if len(g.ApplySplittingRules.Series) == 0 {
		t.Fatal("Felix dump has no series from applySplittingRules/LoadDicom")
	}
	if !g.LocalPropertyProjection.PidFree {
		t.Fatal("localPropertyProjection must be pid-free")
	}
}

// TestFelix_dicomModelTreeDryRun is the G-P0-015 second structural dry run:
// Go consumes the Felix DicomModel golden (G-P0-000 concluded Felix-boot).
// Does not tick G-P0-015; merge + second-person + §5 remain STOP.
func TestFelix_dicomModelTreeDryRun(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-000-felix.json"))
	if err != nil {
		t.Fatal(err)
	}
	var root map[string]any
	if err := json.Unmarshal(raw, &root); err != nil {
		t.Fatal(err)
	}
	if root["caseId"] != "G-P0-000" || root["producer"] != "felix-live-attach" {
		t.Fatalf("case %v producer %v", root["caseId"], root["producer"])
	}

	hp, _ := root["hangingProtocols"].(map[string]any)
	modes, _ := hp["openingViewerModes"].([]any)
	seenMode := map[string]bool{}
	for _, m := range modes {
		s, _ := m.(string)
		seenMode[s] = true
	}
	if !seenMode["NONE"] || !seenMode["ALL_PATIENTS"] || len(modes) != 2 {
		t.Fatalf("OpeningViewer modes %v", modes)
	}

	mime := map[string]int{}
	walkFelixMime(root["explorers"], mime)
	for _, want := range []string{"series/dicom", "pr/dicom", "ko/dicom", "seg/dicom", "sr/dicom"} {
		if mime[want] == 0 {
			t.Fatalf("missing explorer mimeType %s in %v", want, mime)
		}
	}

	hsm, _ := root["hiddenSeriesManager"].(map[string]any)
	s2e, _ := hsm["series2Elements"].(map[string]any)
	var names []string
	for _, v := range s2e {
		arr, _ := v.([]any)
		for _, el := range arr {
			s, _ := el.(string)
			names = append(names, s)
		}
	}
	joined := strings.Join(names, " | ")
	for _, want := range []string{"KOSpecialElement", "PRSpecialElement", "SegSpecialElement"} {
		if !strings.Contains(joined, want) {
			t.Fatalf("HSM missing %s in %q", want, joined)
		}
	}
	if n, _ := hsm["series2ElementsCount"].(float64); int(n) < 3 {
		t.Fatalf("series2ElementsCount %v", hsm["series2ElementsCount"])
	}
}

func walkFelixMime(v any, mime map[string]int) {
	switch t := v.(type) {
	case map[string]any:
		if m, ok := t["mimeType"].(string); ok && m != "" {
			mime[m]++
		}
		for _, child := range t {
			walkFelixMime(child, mime)
		}
	case []any:
		for _, child := range t {
			walkFelixMime(child, mime)
		}
	}
}

func TestDumpMain_headerTextAndUidRole(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-003.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g Golden
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.Header == nil || g.Header.Text == "" || !strings.Contains(g.Header.Text, "GENESIS^PHANTOM") {
		t.Fatalf("HeaderDump dropped text: %+v", g.Header)
	}
	if g.Header.VolatileList != "docs/oracle/volatile-tags.md" {
		t.Fatalf("volatileList %q", g.Header.VolatileList)
	}
	if g.UIDSynthesis == nil || g.UIDSynthesis.Role != "factory-probe-only" {
		t.Fatalf("UIDSynthesis dropped role: %+v", g.UIDSynthesis)
	}
	if g.UIDSynthesis.IngestSite == nil {
		t.Fatal("UIDSynthesis dropped ingestSite")
	}
}

func TestDumpMain_librarySplitAttachProps(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-003.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID        string `json:"caseId"`
		SplitSort struct {
			Status string `json:"status"`
			API    string `json:"api"`
		} `json:"splitSort"`
		SpecialElementAttachment struct {
			Status string `json:"status"`
			API    string `json:"api"`
		} `json:"specialElementAttachment"`
		LocalPropertyResolution struct {
			Status string `json:"status"`
			API    string `json:"api"`
		} `json:"localPropertyResolution"`
		WeasisURIParse struct {
			API              string `json:"api"`
			IsWeasisProtocol bool   `json:"isWeasisProtocol"`
		} `json:"weasisUriParse"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-003" {
		t.Fatalf("G-P0-003.json caseId %q (must match filename)", g.CaseID)
	}
	if g.SplitSort.Status == "unset_pending_felix" || g.SplitSort.API == "" {
		t.Fatalf("splitSort still pending: %#v", g.SplitSort)
	}
	if g.SpecialElementAttachment.Status == "unset_pending_felix" || g.SpecialElementAttachment.API == "" {
		t.Fatalf("attachment still pending: %#v", g.SpecialElementAttachment)
	}
	if g.LocalPropertyResolution.Status == "inventory_only" || g.LocalPropertyResolution.API == "" {
		t.Fatalf("properties still inventory-only: %#v", g.LocalPropertyResolution)
	}
	if !g.WeasisURIParse.IsWeasisProtocol || g.WeasisURIParse.API == "" {
		t.Fatalf("weasisUriParse %#v", g.WeasisURIParse)
	}
}

func TestCorpusHashesPresent(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "hashes.json"))
	if err != nil {
		t.Fatal(err)
	}
	var h struct {
		Count int `json:"count"`
	}
	if err := json.Unmarshal(raw, &h); err != nil {
		t.Fatal(err)
	}
	if h.Count < 40 {
		t.Fatalf("hash inventory too small: %d", h.Count)
	}
}

func TestEdge023_allNamedCases(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-023.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		CaseID              string `json:"caseId"`
		AllNamedCasesPassed bool   `json:"allNamedCasesPassed"`
		HugeNotCommitted    bool   `json:"hugeNotCommitted"`
		Cases               []struct {
			Name string `json:"name"`
			Ok   bool   `json:"ok"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-023" || !g.AllNamedCasesPassed || !g.HugeNotCommitted {
		t.Fatalf("G-P0-023 golden %+v", g)
	}
	if len(g.Cases) != 16 {
		t.Fatalf("want 16 named cases, got %d", len(g.Cases))
	}
	for _, c := range g.Cases {
		if !c.Ok {
			t.Fatalf("named case still failing in golden: %s", c.Name)
		}
	}
	small := []string{
		"G-P0-extra-no-preamble.dcm",
		"G-P0-edge-raw-stream.dcm",
		"G-P0-extra-implicit.dcm",
		"G-P0-edge-undef-sq.dcm",
		"G-P0-edge-odd-length.dcm",
		"G-P0-extra-truncated.dcm",
		"G-P0-edge-no-bot.dcm",
		"G-P0-edge-multi-fragment.dcm",
		"G-P0-edge-12bit.dcm",
		"G-P0-edge-signed-rescale.dcm",
		"G-P0-edge-mono1-plut.dcm",
		"G-P0-codec-jpeg-baseline-us-01.dcm",
		"G-P0-edge-overlay-highbits.dcm",
		"G-P0-edge-private-creator.dcm",
		"G-P0-extra-missing-series.dcm",
		"G-P0-extra-missing-study.dcm",
	}
	dir := filepath.Join("..", "..", "corpus", "phantoms")
	for _, name := range small {
		if _, err := os.Stat(filepath.Join(dir, name)); err != nil {
			t.Fatalf("%s: %v", name, err)
		}
	}
	if _, err := os.Stat(filepath.Join(dir, "G-P0-edge-dicomdir-case", "DICOMDIR")); err != nil {
		t.Fatal(err)
	}
}
