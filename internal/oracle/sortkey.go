package oracle

import (
	"math"
	"time"
)

// SortKeyNames is the 4.7 SortSeriesStack.getValues() order (Messages_en).
// Inner classes: $1 instanceNumber, $2 slicePosition, $3 sliceLocation,
// $5 contentTime, $4 acquisitionTime, $6 diffusionBValue.
// Inverse Stack is SeriesComparator.getReversOrderComparator(), not a seventh name.
var SortKeyNames = []string{
	"Instance Number",
	"Anatomical Direction",
	"Slice Location",
	"Content Time",
	"Acquisition Time",
	"Diffusion b-value",
}

// Signum matches Integer.signum used by SortKeyHarness.
func Signum(v int) int {
	if v < 0 {
		return -1
	}
	if v > 0 {
		return 1
	}
	return 0
}

func cmpNilEither(aNil, bNil bool) (int, bool) {
	if aNil || bNil {
		return 0, true
	}
	return 0, false
}

// CmpInstanceNumber ports SortSeriesStack$1 (Tag (0020,0013) Integer.compareTo).
func CmpInstanceNumber(a, b *int) int {
	if n, done := cmpNilEither(a == nil, b == nil); done {
		return n
	}
	switch {
	case *a < *b:
		return -1
	case *a > *b:
		return 1
	default:
		return 0
	}
}

// doubleCompare ports java.lang.Double.compare (NaN and -0.0 bits).
func doubleCompare(d1, d2 float64) int {
	if d1 < d2 {
		return -1
	}
	if d1 > d2 {
		return 1
	}
	b1 := int64(math.Float64bits(d1))
	b2 := int64(math.Float64bits(d2))
	switch {
	case b1 == b2:
		return 0
	case b1 < b2:
		return -1
	default:
		return 1
	}
}

// CmpSlicePosition ports SortSeriesStack$2 (TagW.SlicePosition + Double.compare).
func CmpSlicePosition(a, b *float64) int {
	if n, done := cmpNilEither(a == nil, b == nil); done {
		return n
	}
	return doubleCompare(*a, *b)
}

// CmpSliceLocation ports SortSeriesStack$3 (Tag (0020,1041) Double.compareTo).
func CmpSliceLocation(a, b *float64) int {
	return CmpSlicePosition(a, b)
}

func clockNanos(t time.Time) int64 {
	h, m, s := t.Clock()
	return int64(h)*int64(time.Hour) + int64(m)*int64(time.Minute) + int64(s)*int64(time.Second) + int64(t.Nanosecond())
}

// CmpLocalTime ports acquisitionTime ($4, (0008,0032)) and contentTime ($5, (0008,0033))
// via java.time.LocalTime.compareTo (clock only, no date).
func CmpLocalTime(a, b *time.Time) int {
	if n, done := cmpNilEither(a == nil, b == nil); done {
		return n
	}
	ca, cb := clockNanos(*a), clockNanos(*b)
	switch {
	case ca < cb:
		return -1
	case ca > cb:
		return 1
	default:
		return 0
	}
}

// CmpDiffusionBValue ports SortSeriesStack$6 (Tag (0018,9087) Double.compareTo).
func CmpDiffusionBValue(a, b *float64) int {
	return CmpSlicePosition(a, b)
}
