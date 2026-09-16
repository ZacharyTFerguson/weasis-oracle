package oracle

// SchemaVersion is the Gate 0a golden document version (G-P0-010).
const SchemaVersion = "genesis.oracle.v1"

// Golden is the versioned document Java and Go must emit and validate.
// LUT-stage / view-state fields wait for Gate 0b (G-P0-018).
type Golden struct {
	SchemaVersion string          `json:"schemaVersion"`
	CaseID        string          `json:"caseId"`
	Class         string          `json:"class"` // BE, BN, ST, BH, PX, AN, PR
	Reference     Pin             `json:"reference"`
	Platform      PlatformStamp   `json:"platform"`
	Header        *HeaderDump     `json:"header,omitempty"`
	RawFrame      *BufferRef      `json:"rawFrame,omitempty"`
	SlicePosition *float64        `json:"slicePosition,omitempty"`
	SplitSort     any             `json:"splitSort,omitempty"`
	WeasisURL                 string          `json:"weasisUrl,omitempty"`
	WeasisURIParse            any             `json:"weasisUriParse,omitempty"`
	SpecialElementAttachment  any             `json:"specialElementAttachment,omitempty"`
	LocalPropertyResolution   any             `json:"localPropertyResolution,omitempty"`
	SplittingRulesSnapshot    any             `json:"splittingRulesSnapshot,omitempty"`
	SortKey                   any             `json:"sortKey,omitempty"`
	StoredPixelData           *BufferRef      `json:"storedPixelData,omitempty"`
	Geometry                  any             `json:"geometry,omitempty"`
	UIDSynthesis  *UIDSynthesis   `json:"uidSynthesis,omitempty"`
}

// UIDSynthesis is the G-P0-051 probe. Non-deterministic createUID → O-P1-011 class ST.
type UIDSynthesis struct {
	API                   string `json:"api"`
	Role                  string `json:"role,omitempty"`
	IngestSite            any    `json:"ingestSite,omitempty"`
	RunA                  string `json:"runA,omitempty"`
	RunB                  string `json:"runB,omitempty"`
	Deterministic         bool   `json:"deterministic"`
	ImpliedClassForOP1011 string `json:"impliedClassForOP1011"`
	Note                  string `json:"note,omitempty"`
}

// Pin is G-P0-001.
type Pin struct {
	WeasisTag           string `json:"weasisTag"`
	WeasisCommit        string `json:"weasisCommit"`
	WeasisCoreImg       string `json:"weasisCoreImg"`
	WeasisDicomTools    string `json:"weasisDicomTools"`
	FelixFramework      string `json:"felixFramework"`
	OpenCVNative        string `json:"opencvNative"`
}

// DefaultPin is frozen from weasis-parent 4.7.0 (tag v4.7.0).
var DefaultPin = Pin{
	WeasisTag:        "v4.7.0",
	WeasisCommit:     "3b3e46c59879ead782e5c474e895befae616a715",
	WeasisCoreImg:    "4.13.0",
	WeasisDicomTools: "5.34.3",
	FelixFramework:   "7.0.5",
	OpenCVNative:     "4.13.0-dcm",
}

// PlatformStamp is G-P0-011.
type PlatformStamp struct {
	OS    string `json:"os"`
	Arch  string `json:"arch"`
	JDK   string `json:"jdk,omitempty"`
	Go    string `json:"go,omitempty"`
	Notes string `json:"notes,omitempty"`
}

// HeaderDump is a canonical-minus-volatile projection (G-P0-049).
type HeaderDump struct {
	Projection   string         `json:"projection"`
	VolatileList string         `json:"volatileList,omitempty"`
	SHA256       string         `json:"sha256,omitempty"`
	Text         string         `json:"text,omitempty"`
	Tags         map[string]any `json:"tags,omitempty"`
}

// BufferRef names a hashed buffer; large pixels may be regenerated in CI (G-P0-029).
type BufferRef struct {
	SHA256   string `json:"sha256,omitempty"`
	Path     string `json:"path,omitempty"`
	Bytes    int    `json:"bytes,omitempty"`
	Width    int    `json:"width,omitempty"`
	Height   int    `json:"height,omitempty"`
	Channels int    `json:"channels,omitempty"`
	Depth    int    `json:"depth,omitempty"`
	Source   string `json:"source,omitempty"`
	Note     string `json:"note,omitempty"`
	Error    string `json:"error,omitempty"`
}
