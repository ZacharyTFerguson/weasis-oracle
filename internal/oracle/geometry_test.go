package oracle

import (
	"encoding/json"
	"math"
	"os"
	"path/filepath"
	"testing"
)

const eps = 1.0e-9

func assertVec(t *testing.T, want, got Vec3) {
	t.Helper()
	if math.Abs(want.X-got.X) > eps || math.Abs(want.Y-got.Y) > eps || math.Abs(want.Z-got.Z) > eps {
		t.Fatalf("vec: want %+v got %+v", want, got)
	}
}

func TestComputeNormalOfSurface_axial(t *testing.T) {
	got := ComputeNormalOfSurface(Vec3{1, 0, 0}, Vec3{0, 1, 0})
	assertVec(t, Vec3{0, 0, 1}, got)
}

func TestComputeNormalOfSurface_sagittal(t *testing.T) {
	got := ComputeNormalOfSurface(Vec3{0, 1, 0}, Vec3{0, 0, 1})
	assertVec(t, Vec3{1, 0, 0}, got)
}

func TestComputeNormalOfSurface_coronal(t *testing.T) {
	got := ComputeNormalOfSurface(Vec3{1, 0, 0}, Vec3{0, 0, 1})
	assertVec(t, Vec3{0, -1, 0}, got)
}

func TestComputeNormalOfSurface_unitLength(t *testing.T) {
	row := Vec3{0.6, 0.8, 0}.normalize()
	col := Vec3{-0.8, 0.6, 0}.normalize()
	n := ComputeNormalOfSurface(row, col)
	if math.Abs(n.length()-1) > eps {
		t.Fatalf("length %v", n.length())
	}
}

func TestComputeNormalOfSurface_parallelZero(t *testing.T) {
	got := ComputeNormalOfSurface(Vec3{1, 0, 0}, Vec3{2, 0, 0})
	assertVec(t, Vec3{0, 0, 0}, got)
}

func TestComputeNormalOfSurfaceFromOrigin_zeroOrigin(t *testing.T) {
	want := ComputeNormalOfSurface(Vec3{1, 0, 0}, Vec3{0, 1, 0})
	got := ComputeNormalOfSurfaceFromOrigin(Vec3{0, 0, 0}, Vec3{1, 0, 0}, Vec3{0, 1, 0})
	assertVec(t, want, got)
}

func TestComputeNormalOfSurfaceFromOrigin_nonzero(t *testing.T) {
	got := ComputeNormalOfSurfaceFromOrigin(Vec3{10, 20, 30}, Vec3{11, 20, 30}, Vec3{10, 21, 30})
	assertVec(t, Vec3{0, 0, 1}, got)
}

func TestOrient_keepsPositiveDominantX(t *testing.T) {
	n := Vec3{0.9, -0.3, 0.2}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{0.9, -0.3, 0.2}, n)
}

func TestOrient_flipsNegativeDominantX(t *testing.T) {
	n := Vec3{-0.9, 0.3, -0.2}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{0.9, -0.3, 0.2}, n)
}

func TestOrient_flipsNegativeDominantY(t *testing.T) {
	n := Vec3{0.2, -0.9, 0.3}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{-0.2, 0.9, -0.3}, n)
}

func TestOrient_flipsNegativeDominantZ(t *testing.T) {
	n := Vec3{0.1, 0.2, -0.95}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{-0.1, -0.2, 0.95}, n)
}

func TestOrient_nil(t *testing.T) {
	if OrientNormalToDominantPositiveAxis(nil) != nil {
		t.Fatal("expected nil")
	}
}

func TestOrient_zeroUnchanged(t *testing.T) {
	n := Vec3{0, 0, 0}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{0, 0, 0}, n)
}

func TestOrient_tieBreakPrefersX(t *testing.T) {
	n := Vec3{-0.5, -0.5, -0.5}
	OrientNormalToDominantPositiveAxis(&n)
	assertVec(t, Vec3{0.5, 0.5, 0.5}, n)
}

func TestSlicePosition_axialIPP(t *testing.T) {
	// IOP axial +Z normal, IPP z=10 → slice position 10 (O-P1-015 dry-run leaf).
	got, ok := SlicePosition([]float64{1, 0, 0, 0, 1, 0}, []float64{0, 0, 10})
	if !ok {
		t.Fatal("expected ok")
	}
	if math.Abs(got-10) > eps {
		t.Fatalf("got %v", got)
	}
}

func TestSlicePosition_matchesWeasisGolden(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "..", "corpus", "goldens", "G-P0-000.json"))
	if err != nil {
		t.Skip(err)
	}
	var g struct {
		SlicePosition float64   `json:"slicePosition"`
		SliceStack    []float64 `json:"sliceStack"`
	}
	if err := json.Unmarshal(raw, &g); err != nil {
		t.Fatal(err)
	}
	got, ok := SlicePosition([]float64{1, 0, 0, 0, 1, 0}, []float64{0, 0, 10})
	if !ok {
		t.Fatal("expected ok")
	}
	if math.Abs(got-g.SlicePosition) > eps {
		t.Fatalf("go %v weasis %v", got, g.SlicePosition)
	}
	for i, z := range []float64{0, 10, 20} {
		p, ok := SlicePosition([]float64{1, 0, 0, 0, 1, 0}, []float64{0, 0, z})
		if !ok {
			t.Fatal("stack")
		}
		if i < len(g.SliceStack) && math.Abs(p-g.SliceStack[i]) > eps {
			t.Fatalf("stack[%d] go %v weasis %v", i, p, g.SliceStack[i])
		}
	}
}
