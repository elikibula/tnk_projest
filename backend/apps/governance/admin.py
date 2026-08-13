from django.contrib import admin
from .models import CommitteeMeeting, CommitteeMember, MeetingDecision, OfficialAppointment, OfficialRole, PersonReference, TrainingActivity, TrainingOutcomeReview, VillageCommittee, VillageVisit
from apps.core.admin import GlobalReferenceAdmin, ProtectedReportLinkedAdmin
admin.site.register(OfficialRole, GlobalReferenceAdmin)
admin.site.register((PersonReference, OfficialAppointment, VillageCommittee, CommitteeMember, CommitteeMeeting, MeetingDecision, VillageVisit, TrainingActivity, TrainingOutcomeReview), ProtectedReportLinkedAdmin)
