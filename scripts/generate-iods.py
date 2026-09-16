#!/usr/bin/env python3
"""Synthetic IODs for G-P0-021 presence (PHI-free). Not JPEG/MPEG codecs."""
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import (
    ExplicitVRLittleEndian,
    generate_uid,
)

root = Path(__file__).resolve().parents[1] / "corpus" / "phantoms"
root.mkdir(parents=True, exist_ok=True)


def meta(sop_class: str, inst: str) -> FileMetaDataset:
    m = FileMetaDataset()
    m.MediaStorageSOPClassUID = sop_class
    m.MediaStorageSOPInstanceUID = inst
    m.TransferSyntaxUID = ExplicitVRLittleEndian
    m.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
    return m


def save(ds: FileDataset, name: str) -> None:
    out = root / name
    ds.save_as(out, write_like_original=False)
    print("wrote", out)


# --- Basic Text SR ---
sop = "1.2.826.0.1.3680043.10.541.21.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.88.11", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.88.11"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.21"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.21.2"
ds.Modality = "SR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-SR"
ds.ValueType = "CONTAINER"
ds.ContinuityOfContent = "SEPARATE"
ds.ConceptNameCodeSequence = Sequence([Dataset()])
ds.ConceptNameCodeSequence[0].CodeValue = "18748-4"
ds.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
ds.ConceptNameCodeSequence[0].CodeMeaning = "Diagnostic Imaging Report"
save(ds, "G-P0-iod-sr.dcm")

# --- KOS ---
sop = "1.2.826.0.1.3680043.10.541.22.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.88.59", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.88.59"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.22.2"
ds.Modality = "KO"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.ValueType = "CONTAINER"
ds.ContinuityOfContent = "SEPARATE"
ds.ConceptNameCodeSequence = Sequence([Dataset()])
ds.ConceptNameCodeSequence[0].CodeValue = "113000"
ds.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
ds.ConceptNameCodeSequence[0].CodeMeaning = "Of Interest"
ref = Dataset()
ref.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
ref.ReferencedSOPInstanceUID = "1.2.826.0.1.3680043.10.541.1.2.2"
ds.CurrentRequestedProcedureEvidenceSequence = Sequence([Dataset()])
ds.CurrentRequestedProcedureEvidenceSequence[0].StudyInstanceUID = ds.StudyInstanceUID
ser = Dataset()
ser.ReferencedSeriesSequence = Sequence([Dataset()])
# keep KOS parseable even if evidence block is thin
save(ds, "G-P0-iod-kos.dcm")

# --- Grayscale Softcopy Presentation State ---
sop = "1.2.826.0.1.3680043.10.541.23.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.11.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.11.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.23.2"
ds.Modality = "PR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.PresentationLUTShape = "IDENTITY"
ref_series = Dataset()
ref_series.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.1.2"
img = Dataset()
img.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
img.ReferencedSOPInstanceUID = "1.2.826.0.1.3680043.10.541.1.2.2"
ref_series.ReferencedImageSequence = Sequence([img])
ds.ReferencedSeriesSequence = Sequence([ref_series])
save(ds, "G-P0-iod-pr.dcm")

# --- 12-lead ECG waveform (minimal) ---
sop = "1.2.826.0.1.3680043.10.541.24.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.9.1.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.9.1.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.24"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.24.2"
ds.Modality = "ECG"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-ECG"
ds.WaveformSequence = Sequence([Dataset()])
w = ds.WaveformSequence[0]
w.WaveformOriginality = "ORIGINAL"
w.NumberOfWaveformChannels = 1
w.NumberOfWaveformSamples = 16
w.SamplingFrequency = 1000
w.WaveformBitsAllocated = 16
w.WaveformSampleInterpretation = "SS"
w.WaveformData = b"\x00\x00" * 16
save(ds, "G-P0-iod-ecg.dcm")

# --- CR MONOCHROME1 ---
sop = "1.2.826.0.1.3680043.10.541.25.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.25"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.25.2"
ds.Modality = "CR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-CR"
ds.Rows = 16
ds.Columns = 16
ds.BitsAllocated = 16
ds.BitsStored = 12
ds.HighBit = 11
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME1"
voi = Dataset()
voi.LUTDescriptor = [3, 0, 16]
voi.LUTData = b"\x00\x00\xff\x7f\xff\xff"
ds.VOILUTSequence = Sequence([voi])
ds.PixelData = b"\x00\x10" * (16 * 16)
save(ds, "G-P0-iod-cr-mono1.dcm")

# --- Palette Color ---
sop = "1.2.826.0.1.3680043.10.541.26.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.7", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.26"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.26.2"
ds.Modality = "OT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-PAL"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "PALETTE COLOR"
ds.RedPaletteColorLookupTableDescriptor = [256, 0, 8]
ds.GreenPaletteColorLookupTableDescriptor = [256, 0, 8]
ds.BluePaletteColorLookupTableDescriptor = [256, 0, 8]
ds.RedPaletteColorLookupTableData = bytes(range(256))
ds.GreenPaletteColorLookupTableData = bytes(range(256))
ds.BluePaletteColorLookupTableData = bytes(range(256))
ds.PixelData = bytes(range(64))
save(ds, "G-P0-iod-palette.dcm")

# --- RGB planar configuration 1 ---
sop = "1.2.826.0.1.3680043.10.541.27.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.7", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.27"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.27.2"
ds.Modality = "OT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-RGB"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "RGB"
ds.PlanarConfiguration = 1
ds.PixelData = b"\x10" * 64 + b"\x20" * 64 + b"\x30" * 64
save(ds, "G-P0-iod-rgb-planar1.dcm")

# --- US multi-frame + region ---
sop = "1.2.826.0.1.3680043.10.541.28.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.3.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.3.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.28"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.28.2"
ds.Modality = "US"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-US"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 2
reg = Dataset()
reg.RegionLocationMinX0 = 0
reg.RegionLocationMinY0 = 0
reg.RegionLocationMaxX1 = 7
reg.RegionLocationMaxY1 = 7
reg.PhysicalUnitsXDirection = 3
reg.PhysicalUnitsYDirection = 3
reg.PhysicalDeltaX = 0.1
reg.PhysicalDeltaY = 0.1
ds.SequenceOfUltrasoundRegions = Sequence([reg])
ds.PixelData = b"\x00" * 64 + b"\xff" * 64
save(ds, "G-P0-iod-us-region.dcm")

# --- NM ---
sop = "1.2.826.0.1.3680043.10.541.29.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.20", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.20"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.29"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.29.2"
ds.Modality = "NM"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-NM"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelData = b"\x00\x01" * 64
save(ds, "G-P0-iod-nm.dcm")

# --- XA cine 2-frame uncompressed ---
sop = "1.2.826.0.1.3680043.10.541.30.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.12.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.12.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.30"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.30.2"
ds.Modality = "XA"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-XA"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 2
ds.CineRate = 15
ds.FrameTime = 66.6
ds.PixelData = b"\x00" * 64 + b"\x7f" * 64
save(ds, "G-P0-iod-xa.dcm")

# --- Enhanced CT (minimal) ---
sop = "1.2.826.0.1.3680043.10.541.31.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.2.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.31"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.31.2"
ds.Modality = "CT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-ENH"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 2
ds.PixelData = b"\x00\x00" * 64 + b"\x01\x00" * 64
save(ds, "G-P0-iod-enhanced-ct.dcm")

# --- Enhanced MR (second Enhanced cell) ---
sop = "1.2.826.0.1.3680043.10.541.32.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.4.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.32"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.32.2"
ds.Modality = "MR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-ENHMR"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 2
ds.PixelData = b"\x00\x00" * 64 + b"\x02\x00" * 64
save(ds, "G-P0-iod-enhanced-mr.dcm")

# --- Uncompressed MR ---
sop = "1.2.826.0.1.3680043.10.541.33.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.4", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.33"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.33.2"
ds.Modality = "MR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-MR"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.ScanningSequence = "GR"
ds.SequenceVariant = "NONE"
ds.ScanOptions = "NONE"
ds.RepetitionTime = 20
ds.EchoTime = 5
ds.FlipAngle = 15
ds.ImagePositionPatient = [0, 0, 0]
ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
ds.PixelData = b"\x00\x10" * 64
save(ds, "G-P0-iod-mr.dcm")

# --- DX MONOCHROME1 ---
sop = "1.2.826.0.1.3680043.10.541.34.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.1.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.34"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.34.2"
ds.Modality = "DX"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-DX"
ds.Rows = 16
ds.Columns = 16
ds.BitsAllocated = 16
ds.BitsStored = 12
ds.HighBit = 11
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME1"
ds.PresentationIntentType = "FOR PRESENTATION"
ds.PixelData = b"\x00\x20" * 256
save(ds, "G-P0-iod-dx.dcm")

# --- PET ---
sop = "1.2.826.0.1.3680043.10.541.35.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.128", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.128"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.35"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.35.2"
ds.Modality = "PT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-PT"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.RescaleIntercept = 0
ds.RescaleSlope = 1
ds.Units = "BQML"
ds.PixelData = b"\x00\x30" * 64
save(ds, "G-P0-iod-pet.dcm")

# --- MG tomosynthesis multi-frame ---
sop = "1.2.826.0.1.3680043.10.541.36.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.13.1.3", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.13.1.3"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.36"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.36.2"
ds.Modality = "MG"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-MG"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 12
ds.HighBit = 11
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 2
ds.ImageLaterality = "R"
ds.PixelData = b"\x00\x00" * 64 + b"\x10\x00" * 64
save(ds, "G-P0-iod-mg-tomo.dcm")

# --- Second PR (GSPS cell min 2) ---
sop = "1.2.826.0.1.3680043.10.541.23.3"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.11.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.11.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.23.4"
ds.Modality = "PR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.PresentationLUTShape = "INVERSE"
g = Dataset()
g.GraphicAnnotationUnits = "PIXEL"
g.GraphicDimensions = 2
g.NumberOfGraphicPoints = 2
g.GraphicData = [0.0, 0.0, 7.0, 7.0]
g.GraphicType = "POLYLINE"
g.GraphicFilled = "N"
ann = Dataset()
ann.GraphicObjectSequence = Sequence([g])
ds.GraphicAnnotationSequence = Sequence([ann])
ref_series = Dataset()
ref_series.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.1.2"
img = Dataset()
img.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
img.ReferencedSOPInstanceUID = "1.2.826.0.1.3680043.10.541.1.2.1"
ref_series.ReferencedImageSequence = Sequence([img])
ds.ReferencedSeriesSequence = Sequence([ref_series])
save(ds, "G-P0-iod-pr-2.dcm")

# --- GSPS covering every graphic type Weasis 4.7 renders (PrGraphicUtil.getGraphicBuilder) ---
def graphic(gtype: str, pts: list[float], filled: str = "N") -> Dataset:
    g = Dataset()
    g.GraphicAnnotationUnits = "PIXEL"
    g.GraphicDimensions = 2
    g.NumberOfGraphicPoints = len(pts) // 2
    g.GraphicData = pts
    g.GraphicType = gtype
    g.GraphicFilled = filled
    return g


COMPOUND_IDS = {
    "MULTILINE": 1,
    "MULTIPOINT": 2,
    "RECTANGLE": 3,
    "RULER": 4,
    "ARROW": 5,
}


def compound(gtype: str, pts: list[float]) -> Dataset:
    c = Dataset()
    c.CompoundGraphicUnits = "PIXEL"
    c.GraphicDimensions = 2
    c.NumberOfGraphicPoints = len(pts) // 2
    c.GraphicData = pts
    c.CompoundGraphicType = gtype
    c.CompoundGraphicInstanceID = COMPOUND_IDS[gtype]
    return c


sop = "1.2.826.0.1.3680043.10.541.23.5"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.11.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.11.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.23.6"
ds.Modality = "PR"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.PresentationLUTShape = "IDENTITY"
ann = Dataset()
ann.GraphicObjectSequence = Sequence(
    [
        graphic("POINT", [1.0, 1.0]),
        graphic("POLYLINE", [0.0, 0.0, 7.0, 7.0]),
        graphic("INTERPOLATED", [0.0, 2.0, 3.0, 5.0, 7.0, 2.0]),
        graphic("CIRCLE", [4.0, 4.0, 6.0, 4.0]),
        graphic("ELLIPSE", [2.0, 4.0, 6.0, 4.0, 4.0, 2.0, 4.0, 6.0]),
    ]
)
ann.CompoundGraphicSequence = Sequence(
    [
        compound("MULTILINE", [0.0, 7.0, 2.0, 5.0, 4.0, 7.0]),
        compound("MULTIPOINT", [1.0, 3.0, 2.0, 3.0, 3.0, 3.0]),
        compound("RECTANGLE", [0.0, 0.0, 3.0, 2.0]),
        compound("RULER", [0.0, 6.0, 6.0, 6.0]),
        compound("ARROW", [0.0, 0.0, 5.0, 5.0]),
    ]
)
ds.GraphicAnnotationSequence = Sequence([ann])
ref_series = Dataset()
ref_series.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.1.2"
img = Dataset()
img.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
img.ReferencedSOPInstanceUID = "1.2.826.0.1.3680043.10.541.1.2.2"
ref_series.ReferencedImageSequence = Sequence([img])
ds.ReferencedSeriesSequence = Sequence([ref_series])
save(ds, "G-P0-iod-pr-gsps-types.dcm")

# --- SEG ---
sop = "1.2.826.0.1.3680043.10.541.37.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.66.4", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.66.4"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.37.2"
ds.Modality = "SEG"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 1
ds.BitsStored = 1
ds.HighBit = 0
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 1
ds.SegmentationType = "BINARY"
seg = Dataset()
seg.SegmentNumber = 1
seg.SegmentLabel = "PHANTOM"
seg.SegmentAlgorithmType = "MANUAL"
code = Dataset()
code.CodeValue = "T-D0050"
code.CodingSchemeDesignator = "SRT"
code.CodeMeaning = "Tissue"
seg.SegmentedPropertyCategoryCodeSequence = Sequence([code])
seg.SegmentedPropertyTypeCodeSequence = Sequence([code])
ds.SegmentSequence = Sequence([seg])
# 8x8x1 bit packed = 8 bytes
ds.PixelData = b"\xff" * 8
save(ds, "G-P0-iod-seg.dcm")

# --- RTSTRUCT ---
sop = "1.2.826.0.1.3680043.10.541.38.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.481.3", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.3"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.38.2"
ds.Modality = "RTSTRUCT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.StructureSetLabel = "PHANTOM"
ds.StructureSetDate = "20200101"
ds.StructureSetTime = "000000"
roi = Dataset()
roi.ROINumber = 1
roi.ReferencedFrameOfReferenceUID = "1.2.826.0.1.3680043.10.541.38.9"
roi.ROIName = "BODY"
ds.StructureSetROISequence = Sequence([roi])
contour = Dataset()
contour.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
contour.ReferencedSOPInstanceUID = "1.2.826.0.1.3680043.10.541.1.2.2"
citem = Dataset()
citem.ContourGeometricType = "CLOSED_PLANAR"
citem.NumberOfContourPoints = 3
citem.ContourData = [0, 0, 10, 10, 0, 10, 0, 10, 10]
citem.ContourImageSequence = Sequence([contour])
cs = Dataset()
cs.ReferencedROINumber = 1
cs.ContourSequence = Sequence([citem])
ds.ROIContourSequence = Sequence([cs])
save(ds, "G-P0-iod-rtstruct.dcm")

# --- RTSTRUCT with (3006,0010) FOR chain (4.7 StructureSet.initReferences) ---
sop = "1.2.826.0.1.3680043.10.541.38.93"
ds = FileDataset(
    str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.481.3", sop), preamble=b"\0" * 128
)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.3"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.38.93.2"
ds.Modality = "RTSTRUCT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.StructureSetLabel = "PHANTOM"
ds.StructureSetDate = "20200101"
ds.StructureSetTime = "000000"
for_uid = "1.2.826.0.1.3680043.10.541.1.52"
ct_series = "1.2.826.0.1.3680043.10.541.1.2"
ct_sop = "1.2.826.0.1.3680043.10.541.1.2.2"
img = Dataset()
img.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
img.ReferencedSOPInstanceUID = ct_sop
rt_ser = Dataset()
rt_ser.SeriesInstanceUID = ct_series
rt_ser.ContourImageSequence = Sequence([img])
rt_stu = Dataset()
rt_stu.ReferencedSOPClassUID = "1.2.840.10008.3.1.2.3.1"
rt_stu.ReferencedSOPInstanceUID = ds.StudyInstanceUID
rt_stu.RTReferencedSeriesSequence = Sequence([rt_ser])
for_item = Dataset()
for_item.FrameOfReferenceUID = for_uid
for_item.RTReferencedStudySequence = Sequence([rt_stu])
ds.ReferencedFrameOfReferenceSequence = Sequence([for_item])
roi = Dataset()
roi.ROINumber = 1
roi.ReferencedFrameOfReferenceUID = for_uid
roi.ROIName = "BODY"
ds.StructureSetROISequence = Sequence([roi])
contour = Dataset()
contour.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
contour.ReferencedSOPInstanceUID = ct_sop
citem = Dataset()
citem.ContourGeometricType = "CLOSED_PLANAR"
citem.NumberOfContourPoints = 3
citem.ContourData = [0, 0, 10, 10, 0, 10, 0, 10, 10]
citem.ContourImageSequence = Sequence([contour])
cs = Dataset()
cs.ReferencedROINumber = 1
cs.ContourSequence = Sequence([citem])
ds.ROIContourSequence = Sequence([cs])
save(ds, "G-P0-iod-rtstruct-for.dcm")

# --- RTDOSE ---
sop = "1.2.826.0.1.3680043.10.541.39.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.481.2", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.2"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.39.2"
ds.Modality = "RTDOSE"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.DoseUnits = "GY"
ds.DoseType = "PHYSICAL"
ds.DoseSummationType = "PLAN"
ds.NumberOfFrames = 1
ds.GridFrameOffsetVector = [0]
ds.PixelData = b"\x00\x40" * 64
save(ds, "G-P0-iod-rtdose.dcm")

# --- RTPLAN ---
sop = "1.2.826.0.1.3680043.10.541.40.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.481.5", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.5"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.40.2"
ds.Modality = "RTPLAN"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.RTPlanLabel = "PHANTOM"
ds.RTPlanDate = "20200101"
ds.RTPlanTime = "000000"
beam = Dataset()
beam.BeamNumber = 1
beam.BeamName = "AP"
beam.BeamType = "STATIC"
beam.RadiationType = "PHOTON"
ds.BeamSequence = Sequence([beam])
save(ds, "G-P0-iod-rtplan.dcm")

# --- AU encapsulated wav ---
sop = "1.2.826.0.1.3680043.10.541.41.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.104.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.104.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.41"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.41.2"
ds.Modality = "AU"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-AU"
ds.MIMETypeOfEncapsulatedDocument = "audio/wav"
# minimal PCM wav header + 8 zero samples
wav = (
    b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    b"D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x10\x00\x00\x00"
    + b"\x00\x00" * 8
)
ds.EncapsulatedDocument = wav
save(ds, "G-P0-iod-au.dcm")

# --- Float parametric map ---
sop = "1.2.826.0.1.3680043.10.541.42.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.30", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.30"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.42"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.42.2"
ds.Modality = "OT"
ds.ImageType = ["DERIVED", "PRIMARY", "ADC"]
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-PMAP"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 32
ds.BitsStored = 32
ds.HighBit = 31
ds.PixelRepresentation = 1
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.NumberOfFrames = 1
import struct

ds.FloatPixelData = b"".join(struct.pack("<f", float(i)) for i in range(64))
save(ds, "G-P0-iod-pmap-float.dcm")

# --- 8-bit US RGB for JPEG baseline (source, also a presence object) ---
sop = "1.2.826.0.1.3680043.10.541.43.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.6.1", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.43"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.43.2"
ds.Modality = "US"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-USRGB"
ds.Rows = 16
ds.Columns = 16
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "RGB"
ds.PlanarConfiguration = 0
ds.PixelData = bytes((i % 256) for i in range(16 * 16 * 3))
save(ds, "G-P0-iod-us-rgb.dcm")

# --- Charset UTF-8 + IR 87 + multi-valued ---
sop = "1.2.826.0.1.3680043.10.541.44.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.2", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.44"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.44.2"
ds.Modality = "CT"
ds.SpecificCharacterSet = "ISO_IR 192"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-UTF8"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelData = b"\x00\x01" * 64
save(ds, "G-P0-iod-utf8.dcm")

sop = "1.2.826.0.1.3680043.10.541.45.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.2", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.45"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.45.2"
ds.Modality = "CT"
ds.SpecificCharacterSet = "ISO 2022 IR 87"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-IR87"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelData = b"\x00\x01" * 64
save(ds, "G-P0-iod-ir87.dcm")

sop = "1.2.826.0.1.3680043.10.541.46.1"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.2", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.46"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.46.2"
ds.Modality = "CT"
ds.SpecificCharacterSet = ["ISO 2022 IR 6", "ISO 2022 IR 87"]
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-CSMULTI"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelData = b"\x00\x01" * 64
save(ds, "G-P0-iod-charset-multi.dcm")

# --- Split-rule pair: same series UID as phantom CT, different ConvolutionKernel ---
sop = "1.2.826.0.1.3680043.10.541.1.2.99"
ds = FileDataset(str(root / "x"), {}, file_meta=meta("1.2.840.10008.5.1.4.1.1.2", sop), preamble=b"\0" * 128)
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.1.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.1.2"
ds.Modality = "CT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-001"
ds.ConvolutionKernel = "BONE"
ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
ds.Rows = 16
ds.Columns = 16
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelSpacing = [1.0, 1.0]
ds.ImagePositionPatient = [0.0, 0.0, 30.0]
ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
ds.InstanceNumber = 99
ds.PixelData = b"\xff\x00" * 256
save(ds, "G-P0-split-bone.dcm")

print("iods done")
