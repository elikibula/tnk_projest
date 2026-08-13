from django.db.models import Q, QuerySet
from apps.locations.models import Village

def villages_for_user(user) -> QuerySet[Village]:
    if user.is_superuser:
        return Village.objects.all()
    assignments = user.location_assignments.filter(is_active=True)
    return Village.objects.filter(Q(pk__in=assignments.values("village_id")) | Q(tikina_id__in=assignments.values("tikina_id")) | Q(tikina__province_id__in=assignments.values("province_id"))).distinct()
