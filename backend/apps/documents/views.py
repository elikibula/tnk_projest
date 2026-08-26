import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from apps.audit.services import record_event
from apps.core.security import can_view_document
from .models import EvidenceDocument


@login_required
def photo_preview(request, document_uuid):
    from io import BytesIO
    from PIL import Image, ImageOps
    from django.http import Http404, HttpResponse

    document = get_object_or_404(EvidenceDocument, uuid=document_uuid)
    if not can_view_document(request.user, document):
        raise PermissionDenied("You cannot view this photo.")
    from pathlib import Path
    if Path(document.file.name).suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise Http404("Photo preview unavailable.")
    try:
        with document.file.open("rb") as source, Image.open(source) as original:
            preview = ImageOps.exif_transpose(original)
            preview.thumbnail((1600, 1600) if request.GET.get("full") == "1" else (420, 300))
            output = BytesIO()
            preview.convert("RGB").save(output, format="JPEG", quality=85)
    except (OSError, ValueError, Image.DecompressionBombError):
        raise Http404("Photo preview unavailable.")
    response = HttpResponse(output.getvalue(), content_type="image/jpeg")
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    record_event(actor=request.user, action="document.accessed", instance=document, summary="Viewed record photo preview")
    return response


evidence_logger = logging.getLogger("tnk.evidence")
@login_required
def download(request,document_uuid):
    document=get_object_or_404(EvidenceDocument,uuid=document_uuid)
    if not can_view_document(request.user, document):
        evidence_logger.warning(
            "Evidence access rejected",
            extra={"event": "evidence.denied", "request_id": getattr(request, "request_id", "")},
        )
        raise PermissionDenied("Your role, location, or confidentiality clearance does not allow access to this evidence.")
    record_event(actor=request.user,action="document.accessed",instance=document,summary=f"Accessed {document.title}",metadata={"ip_address":request.META.get("REMOTE_ADDR"),"user_agent":request.META.get("HTTP_USER_AGENT","")})
    response = FileResponse(document.file.open("rb"),as_attachment=True,filename=document.original_filename)
    response["Cache-Control"] = "private, no-store"
    return response
