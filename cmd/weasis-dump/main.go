package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/ZacharyTFerguson/weasis-oracle/internal/oracle"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "dump":
		os.Exit(dump(os.Args[2:]))
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintf(os.Stderr, `weasis-dump — Gate 0a headless emitter (G-P0-012 spec; dry-run leaf only)

  weasis-dump dump slice-position --iop 1,0,0,0,1,0 --ipp 0,0,10 --case-id O-P1-015
  weasis-dump dump sort-key

Full DICOM file dump is O-P1-023 (Phase 1). sort-key is the G-P0-015 vertical
dry-run leaf (Weasis SortSeriesStack order + comparator signs).
`)
}

func dump(args []string) int {
	if len(args) < 1 {
		usage()
		return 2
	}
	switch args[0] {
	case "slice-position":
		return dumpSlicePosition(args[1:])
	case "sort-key":
		return dumpSortKey()
	default:
		usage()
		return 2
	}
}

func dumpSortKey() int {
	g := map[string]any{
		"schemaVersion": oracle.SchemaVersion,
		"caseId":        "G-P0-015",
		"class":         "ST",
		"reference":     oracle.DefaultPin,
		"sortKey": map[string]any{
			"api":         "org.weasis.dicom.codec.SortSeriesStack",
			"comparators": oracle.SortKeyNames,
			"pairs": []map[string]any{
				{"id": "instanceNumber_low_high", "key": "instanceNumber", "cmp": oracle.Signum(oracle.CmpInstanceNumber(pi(1), pi(5)))},
				{"id": "instanceNumber_high_low", "key": "instanceNumber", "cmp": oracle.Signum(oracle.CmpInstanceNumber(pi(5), pi(1)))},
				{"id": "instanceNumber_equal", "key": "instanceNumber", "cmp": oracle.CmpInstanceNumber(pi(7), pi(7))},
				{"id": "instanceNumber_null_left", "key": "instanceNumber", "cmp": oracle.CmpInstanceNumber(nil, pi(3))},
				{"id": "slicePosition_back_front", "key": "slicePosition", "cmp": oracle.Signum(oracle.CmpSlicePosition(pf(-50), pf(50)))},
				{"id": "slicePosition_null_left", "key": "slicePosition", "cmp": oracle.CmpSlicePosition(nil, pf(12.5))},
				{"id": "sliceLocation_low_high", "key": "sliceLocation", "cmp": oracle.Signum(oracle.CmpSliceLocation(pf(10), pf(20)))},
				{"id": "contentTime_early_late", "key": "contentTime", "cmp": oracle.Signum(oracle.CmpLocalTime(pt(12, 0, 0), pt(12, 0, 5)))},
				{"id": "acquisitionTime_early_late", "key": "acquisitionTime", "cmp": oracle.Signum(oracle.CmpLocalTime(pt(8, 30, 0), pt(8, 30, 30)))},
				{"id": "diffusionBValue_b0_b1000", "key": "diffusionBValue", "cmp": oracle.Signum(oracle.CmpDiffusionBValue(pf(0), pf(1000)))},
			},
		},
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(g); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return 0
}

func pi(v int) *int {
	return &v
}
func pf(v float64) *float64 {
	return &v
}
func pt(h, m, s int) *time.Time {
	t := time.Date(1970, 1, 1, h, m, s, 0, time.UTC)
	return &t
}

func dumpSlicePosition(args []string) int {
	fs := flag.NewFlagSet("slice-position", flag.ExitOnError)
	iopS := fs.String("iop", "", "ImageOrientationPatient, 6 comma-separated floats")
	ippS := fs.String("ipp", "", "ImagePositionPatient, 3 comma-separated floats")
	caseID := fs.String("case-id", "O-P1-015", "oracle case id")
	_ = fs.Parse(args)
	iop, err := parseFloats(*iopS, 6)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	ipp, err := parseFloats(*ippS, 3)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	pos, ok := oracle.SlicePosition(iop, ipp)
	if !ok {
		fmt.Fprintln(os.Stderr, "slice-position: missing IOP/IPP")
		return 1
	}
	g := oracle.Golden{
		SchemaVersion: oracle.SchemaVersion,
		CaseID:        *caseID,
		Class:         "ST",
		Reference:     oracle.DefaultPin,
		SlicePosition: &pos,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(g); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return 0
}

func parseFloats(s string, n int) ([]float64, error) {
	parts := strings.Split(s, ",")
	if len(parts) != n {
		return nil, fmt.Errorf("want %d floats, got %q", n, s)
	}
	out := make([]float64, n)
	for i, p := range parts {
		v, err := strconv.ParseFloat(strings.TrimSpace(p), 64)
		if err != nil {
			return nil, err
		}
		out[i] = v
	}
	return out, nil
}
