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
