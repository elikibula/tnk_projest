from pathlib import Path
import zipfile
from django.conf import settings
from django.core.exceptions import ValidationError
ALLOWED_EXTENSIONS={".pdf",".jpg",".jpeg",".png",".docx",".xlsx"}


def detected_extension(value):
    position = value.tell() if hasattr(value, "tell") else 0
    try:
        value.seek(0)
        header = value.read(12)
        if header.startswith(b"%PDF-"):
            return ".pdf"
        if header.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        if header.startswith(b"PK"):
            value.seek(0)
            try:
                with zipfile.ZipFile(value) as archive:
                    names = set(archive.namelist())
            except (zipfile.BadZipFile, OSError):
                return None
            if "word/document.xml" in names:
                return ".docx"
            if "xl/workbook.xml" in names:
                return ".xlsx"
        return None
    finally:
        value.seek(position)


def validate_evidence_file(value):
    extension = Path(value.name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS: raise ValidationError("Unsupported evidence file type.")
    if value.size > settings.TNK_MAX_UPLOAD_BYTES: raise ValidationError("Evidence file exceeds the maximum allowed size.")
    detected = detected_extension(value)
    equivalent = {".jpeg": ".jpg"}.get(extension, extension)
    if detected != equivalent:
        raise ValidationError("The file content does not match its filename. Upload a valid PDF, image, Word, or Excel file.")
