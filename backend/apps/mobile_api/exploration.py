"""Read-only mobile hierarchy and analytics using existing scope/calculation rules."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics import decision_support as analytics
from apps.core.security import can_view_analytics
from apps.locations.models import Province, Tikina
from apps.reporting.models import ReportingPeriod
from .serializers import ReportingPeriodSerializer


class MobilePage(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class OptionalMobilePage(MobilePage):
    def paginate_queryset(self, queryset, request, view=None):
        if "page" not in request.query_params and "page_size" not in request.query_params:
            return None  # Older clients expect a JSON array.
        return super().paginate_queryset(queryset, request, view)


class ScopeQuery(serializers.Serializer):
    level = serializers.ChoiceField(choices=("province", "tikina", "village"), default="province")
    parent = serializers.UUIDField(required=False)
    q = serializers.CharField(required=False, max_length=120, allow_blank=True)


def location_payload(location):
    return {"uuid": str(location.uuid), "name": location.name_en,
            "name_fj": location.name_fj, "level": location._meta.model_name}


def scoped_locations(user):
    villages = analytics.scoped_villages(user).filter(tikina__is_active=True, tikina__province__is_active=True)
    return {"village": villages,
            "tikina": Tikina.objects.filter(villages__in=villages).distinct(),
            "province": Province.objects.filter(tikina__villages__in=villages).distinct()}


class LocationDirectoryView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        query = ScopeQuery(data=request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        level = values["level"]
        scopes = scoped_locations(request.user)
        rows = scopes[level]
        if values.get("parent"):
            if level == "province":
                raise serializers.ValidationError({"parent": "Provinces do not accept a parent."})
            parent_level = "province" if level == "tikina" else "tikina"
            parent = get_object_or_404(scopes[parent_level], uuid=values["parent"])
            rows = rows.filter(**{parent_level: parent})
        if values.get("q"):
            rows = rows.filter(Q(name_en__icontains=values["q"]) | Q(name_fj__icontains=values["q"]))
        page = MobilePage()
        items = page.paginate_queryset(rows.order_by("name_en", "pk"), request)
        return page.get_paginated_response([location_payload(item) for item in items])


class AnalyticsQuery(serializers.Serializer):
    level = serializers.ChoiceField(choices=("national", "province", "tikina", "village"), required=False)
    location = serializers.UUIDField(required=False)
    period = serializers.UUIDField(required=False)
    compare_period = serializers.UUIDField(required=False)


def metric_payload(data):
    return {"reporting": data["reporting"], "indicators": data["indicators"]}


class AnalyticsOverviewView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        if not can_view_analytics(request.user):
            raise PermissionDenied("Your role cannot view analytics.")
        query = AnalyticsQuery(data=request.query_params)
        query.is_valid(raise_exception=True)
        values = query.validated_data
        scopes = scoped_locations(request.user)
        level = values.get("level")
        scope = None
        if level == "national":
            if not analytics.can_view_national(request.user):
                raise PermissionDenied("National analytics is not permitted.")
        elif level:
            if not values.get("location"):
                raise serializers.ValidationError({"location": "A location UUID is required."})
            scope = get_object_or_404(scopes[level], uuid=values["location"])
        elif not analytics.can_view_national(request.user):
            scope = scopes["province"].order_by("name_en").first()
            if scope is None:
                raise PermissionDenied("No assigned analytics scope.")
        periods = ReportingPeriod.objects.order_by("-year", "-quarter")
        period = get_object_or_404(periods, uuid=values["period"]) if values.get("period") else analytics.selected_period(None)
        if period is None:
            return Response({"period": None, "scope": location_payload(scope) if scope else None,
                             "summary": None, "children": [], "insights": [], "trends": [], "periods": []})
        previous = (get_object_or_404(periods, uuid=values["compare_period"]) if values.get("compare_period")
                    else periods.filter(start_date__lt=period.start_date).first())
        current = analytics.summary(request.user, period, scope)
        old = analytics.summary(request.user, previous, scope) if previous else None
        page = MobilePage()
        children = page.paginate_queryset(analytics.child_locations(request.user, scope), request)
        missing = analytics.missing_reports(request.user, period, scope)
        scoped = analytics.scoped_villages(request.user)
        if isinstance(scope, Province):
            scoped = scoped.filter(tikina__province=scope)
        elif isinstance(scope, Tikina):
            scoped = scoped.filter(tikina=scope)
        elif scope is not None:
            scoped = scoped.filter(pk=scope.pk)
        return Response({
            "server_time": timezone.now(), "period": ReportingPeriodSerializer(period).data,
            "periods": ReportingPeriodSerializer(periods, many=True).data,
            "scope": location_payload(scope) if scope else {"level": "national", "uuid": None, "name": "Fiji"},
            "summary": metric_payload(current),
            "comparison": {"period": ReportingPeriodSerializer(previous).data, **metric_payload(old)} if old else None,
            "children": [{"location": location_payload(child), **metric_payload(analytics.summary(request.user, period, child))} for child in children],
            "children_count": page.page.paginator.count, "next": page.get_next_link(),
            "insights": analytics.insights(current, old), "trends": analytics.trends(request.user, scope),
            "missing_reports": [{
                "village": location_payload(item["village"]),
                "last_period": str(item["last_report"].reporting_period) if item["last_report"] else None,
            } for item in missing],
            "map_villages": [{
                **location_payload(village),
                "latitude": village.latitude,
                "longitude": village.longitude,
            } for village in scoped.exclude(latitude__isnull=True).exclude(longitude__isnull=True)],
            "data_scope": "Official indicators use approved, locked and archived reports. Compliance includes received reports.",
        })
