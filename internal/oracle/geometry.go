package oracle

import "math"

// Vec3 is a float64 triple. Products are computed in float64 with named
// intermediates so FMA fusion is not required for the Gate 0a dry-run leaf.
type Vec3 struct {
	X, Y, Z float64
}

func (v Vec3) add(o Vec3) Vec3 { return Vec3{v.X + o.X, v.Y + o.Y, v.Z + o.Z} }
func (v Vec3) sub(o Vec3) Vec3 { return Vec3{v.X - o.X, v.Y - o.Y, v.Z - o.Z} }
func (v Vec3) scale(s float64) Vec3 {
	return Vec3{v.X * s, v.Y * s, v.Z * s}
}
func (v Vec3) negate() Vec3 { return Vec3{-v.X, -v.Y, -v.Z} }

func (v Vec3) dot(o Vec3) float64 {
	px := v.X * o.X
	py := v.Y * o.Y
	pz := v.Z * o.Z
	return px + py + pz
}

func (v Vec3) cross(o Vec3) Vec3 {
	x := v.Y*o.Z - v.Z*o.Y
	y := v.Z*o.X - v.X*o.Z
	z := v.X*o.Y - v.Y*o.X
	return Vec3{x, y, z}
}

func (v Vec3) lengthSquared() float64 {
	return v.dot(v)
}

func (v Vec3) length() float64 {
	return math.Sqrt(v.lengthSquared())
}

func (v Vec3) normalize() Vec3 {
	ls := v.lengthSquared()
	if ls == 0 {
		return v
	}
	inv := 1.0 / math.Sqrt(ls)
	return v.scale(inv)
}

// ComputeNormalOfSurface ports Weasis VectorUtils.computeNormalOfSurface(v1, v2):
// cross then normalize if lengthSquared > 0.
func ComputeNormalOfSurface(v1, v2 Vec3) Vec3 {
	n := v1.cross(v2)
	if n.lengthSquared() > 0.0 {
		return n.normalize()
	}
	return n
}

// ComputeNormalOfSurfaceFromOrigin ports the three-point overload.
func ComputeNormalOfSurfaceFromOrigin(origin, v1, v2 Vec3) Vec3 {
	u := v1.sub(origin)
	w := v2.sub(origin)
	n := u.cross(w)
	if n.lengthSquared() > 0.0 {
		return n.normalize()
	}
	return n
}

// OrientNormalToDominantPositiveAxis ports
// VectorUtils.orientNormalToDominantPositiveAxis. Tie-break: |x| >= |y| && |x| >= |z|
// prefers X, else |y| >= |z| prefers Y, else Z. Flips if that component is < 0.
func OrientNormalToDominantPositiveAxis(normal *Vec3) *Vec3 {
	if normal == nil {
		return nil
	}
	ax := math.Abs(normal.X)
	ay := math.Abs(normal.Y)
	az := math.Abs(normal.Z)
	var dominant float64
	if ax >= ay && ax >= az {
		dominant = normal.X
	} else if ay >= az {
		dominant = normal.Y
	} else {
		dominant = normal.Z
	}
	if dominant < 0 {
		*normal = normal.negate()
	}
	return normal
}

// RowAndColumnFromIOP splits ImageOrientationPatient (6 doubles) the way
// Weasis ImageOrientation.getRowImagePosition / getColumnImagePosition do.
func RowAndColumnFromIOP(iop []float64) (row, col Vec3, ok bool) {
	if len(iop) != 6 {
		return Vec3{}, Vec3{}, false
	}
	return Vec3{iop[0], iop[1], iop[2]}, Vec3{iop[3], iop[4], iop[5]}, true
}

// ComputeImageNormal ports DicomMediaUtils.computeImageNormal.
func ComputeImageNormal(iop []float64) *Vec3 {
	row, col, ok := RowAndColumnFromIOP(iop)
	if !ok {
		return nil
	}
	n := ComputeNormalOfSurface(row, col)
	return OrientNormalToDominantPositiveAxis(&n)
}

// SlicePosition ports DicomMediaUtils.computeSlicePosition when IPP and IOP
// are present: dot(normal, IPP). Caller should pass SliceLocation fallback
// when this returns false.
func SlicePosition(iop, ipp []float64) (float64, bool) {
	if len(ipp) != 3 {
		return 0, false
	}
	n := ComputeImageNormal(iop)
	if n == nil {
		return 0, false
	}
	pos := Vec3{ipp[0], ipp[1], ipp[2]}
	return n.dot(pos), true
}
