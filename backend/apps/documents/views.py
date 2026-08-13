import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from apps.audit.services import record_event
from apps.core.security import can_view_document
from .models import EvidenceDocument


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
    return FileResponse(document.file.open("rb"),as_attachment=True,filename=document.original_filename)
