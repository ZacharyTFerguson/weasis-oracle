# Canonical-minus-volatile tags (G-P0-049)

Strip or placeholder these before a `BE` hash of a header or Part 10 object:

| Tag | Name | Action |
| --- | --- | --- |
| (0002,0012) | Implementation Class UID | placeholder |
| (0002,0013) | Implementation Version Name | placeholder |
| (0008,0012) | Instance Creation Date | strip |
| (0008,0013) | Instance Creation Time | strip |
| (0008,0014) | Instance Creator UID | placeholder |
| (0008,0018) | SOP Instance UID | placeholder (unless content-derived; see G-P0-051) |
| (0020,000D) | Study Instance UID | placeholder |
| (0020,000E) | Series Instance UID | placeholder |
| (0008,0020) | Study Date | strip unless case needs it |
| (0008,0030) | Study Time | strip unless case needs it |
| AE titles we generate | | placeholder |

This list is the only volatile set used by `CanonicalHeader` and `HeaderDump`. Identity tags (PatientName/ID, AccessionNumber, InstitutionName, StationName, MediaStorageSOPInstanceUID) stay in the dump. Pixel bulk is skipped separately.
