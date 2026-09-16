package oracle

import (
	"encoding/json"
	"math"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func i(v int) *int         { return &v }
func f(v float64) *float64 { return &v }
func tms(h, m, s int) time.Time {
	return time.Date(1970, 1, 1, h, m, s, 0, time.UTC)
}

func TestCmpInstanceNumber_ordersAndNull(t *testing.T) {
	if Signum(CmpInstanceNumber(i(1), i(5))) != -1 {
		t.Fatal("1 < 5")
	}
	if Signum(CmpInstanceNumber(i(5), i(1))) != 1 {
		t.Fatal("5 > 1")
	}
	if CmpInstanceNumber(i(7), i(7)) != 0 {
		t.Fatal("equal")
	}
	if CmpInstanceNumber(nil, i(3)) != 0 || CmpInstanceNumber(i(3), nil) != 0 {
		t.Fatal("null either side is 0")
	}
}

func TestCmpSlicePosition_ordersAndNull(t *testing.T) {
	if Signum(CmpSlicePosition(f(-50), f(50))) != -1 {
		t.Fatal("back < front")
	}
	if CmpSlicePosition(nil, f(12.5)) != 0 {
		t.Fatal("null")
	}
}

func TestDoubleCompare_matchesJava(t *testing.T) {
	nan := math.NaN()
	n0 := math.Copysign(0, -1)
	p0 := 0.0
	if Signum(CmpSlicePosition(&nan, f(1))) != 1 {
		t.Fatal("NaN vs 1")
	}
	if Signum(CmpSlicePosition(f(1), &nan)) != -1 {
		t.Fatal("1 vs NaN")
	}
	if CmpSlicePosition(&nan, &nan) != 0 {
		t.Fatal("NaN vs NaN")
	}
	if Signum(CmpSlicePosition(&n0, &p0)) != -1 {
		t.Fatal("-0 vs +0")
	}
	if Signum(CmpSlicePosition(&p0, &n0)) != 1 {
		t.Fatal("+0 vs -0")
	}
}

func TestCmpLocalTime_clockOnly(t *testing.T) {
	a := time.Date(1999, 12, 31, 12, 0, 0, 0, time.UTC)
	b := time.Date(2001, 1, 1, 12, 0, 5, 0, time.UTC)
	if Signum(CmpLocalTime(&a, &b)) != -1 {
		t.Fatal("same-clock compare must ignore date")
	}
	sameClock := time.Date(2020, 6, 1, 12, 0, 0, 0, time.UTC)
	if CmpLocalTime(&a, &sameClock) != 0 {
		t.Fatal("identical LocalTime on different dates")
	}
}

func TestCmpTimesAndBValue(t *testing.T) {
	a := tms(12, 0, 0)
	b := tms(12, 0, 5)
	if Signum(CmpLocalTime(&a, &b)) != -1 {
		t.Fatal("content time")
	}
	early := tms(8, 30, 0)
	late := tms(8, 30, 30)
	if Signum(CmpLocalTime(&early, &late)) != -1 {
		t.Fatal("acquisition time")
	}
	if Signum(CmpDiffusionBValue(f(0), f(1000))) != -1 {
		t.Fatal("b-value")
	}
}

func TestSortKeyGolden_matchesGoLeaf(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-015.json"))
	if err != nil {
		t.Fatal(err)
	}
	var g struct {
		SchemaVersion string `json:"schemaVersion"`
		CaseID        string `json:"caseId"`
		Class         string `json:"class"`
		SortKey       struct {
			API         string   `json:"api"`
			Comparators []string `json:"comparators"`
			Pairs       []struct {
				ID  string `json:"id"`
				Key string `json:"key"`
				Cmp int    `json:"cmp"`
			} `json:"pairs"`
		} `json:"sortKey"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	if g.CaseID != "G-P0-015" || g.Class != "ST" || g.SchemaVersion != SchemaVersion {
		t.Fatalf("header %+v", g)
	}
	if g.SortKey.API != "org.weasis.dicom.codec.SortSeriesStack" {
		t.Fatalf("api %q", g.SortKey.API)
	}
	if len(g.SortKey.Comparators) != 6 {
		t.Fatalf("comparators %v", g.SortKey.Comparators)
	}
	for i, name := range SortKeyNames {
		if g.SortKey.Comparators[i] != name {
			t.Fatalf("comparator %d: want %q got %q", i, name, g.SortKey.Comparators[i])
		}
	}
	got := map[string]int{}
	for _, p := range g.SortKey.Pairs {
		got[p.ID] = p.Cmp
	}
	want := map[string]int{
		"instanceNumber_low_high":    Signum(CmpInstanceNumber(i(1), i(5))),
		"instanceNumber_high_low":    Signum(CmpInstanceNumber(i(5), i(1))),
		"instanceNumber_equal":       CmpInstanceNumber(i(7), i(7)),
		"instanceNumber_null_left":   CmpInstanceNumber(nil, i(3)),
		"slicePosition_back_front":   Signum(CmpSlicePosition(f(-50), f(50))),
		"slicePosition_null_left":    CmpSlicePosition(nil, f(12.5)),
		"sliceLocation_low_high":     Signum(CmpSliceLocation(f(10), f(20))),
		"contentTime_early_late":     Signum(CmpLocalTime(ptrTime(tms(12, 0, 0)), ptrTime(tms(12, 0, 5)))),
		"acquisitionTime_early_late": Signum(CmpLocalTime(ptrTime(tms(8, 30, 0)), ptrTime(tms(8, 30, 30)))),
		"diffusionBValue_b0_b1000":   Signum(CmpDiffusionBValue(f(0), f(1000))),
	}
	for id, w := range want {
		if got[id] != w {
			t.Errorf("%s: golden %d want %d", id, got[id], w)
		}
	}
	if len(got) != len(want) {
		t.Fatalf("pair count golden %d want %d", len(got), len(want))
	}
}

func ptrTime(v time.Time) *time.Time { return &v }
