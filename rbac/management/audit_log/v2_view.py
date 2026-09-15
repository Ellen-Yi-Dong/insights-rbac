#
# Copyright 2026 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""View for the Audit Log V2 API."""

from management.audit_log.model import AuditLog
from management.audit_log.v2_serializer import (
    AuditLogV2ListInputSerializer,
    AuditLogV2OutputSerializer,
    validate_fields_parameter,
)
from management.base_viewsets import BaseV2ViewSet
from management.permissions.auditlog_v2_access import AuditLogV2KesselAccessPermission
from management.utils import filter_queryset_by_tenant
from management.v2_filters import v2_name_filter

from api.common.pagination import V2CursorPagination


class AuditLogV2CursorPagination(V2CursorPagination):
    """Cursor pagination for audit logs, newest entry first."""

    ordering = "-created"
    FIELD_MAPPING = {"created": "created"}


class AuditLogV2ViewSet(BaseV2ViewSet):
    """Read-only V2 ViewSet for audit logs.

    Only the list action is routed; individual entries are not addressable because
    audit log rows have no UUID identity of their own.
    """

    permission_classes = (AuditLogV2KesselAccessPermission,)
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogV2OutputSerializer
    pagination_class = AuditLogV2CursorPagination
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        """Return the requesting tenant's audit log entries, newest first."""
        return filter_queryset_by_tenant(AuditLog.objects.all(), self.request.tenant).order_by("-created")

    def list(self, request, *args, **kwargs):
        """List the tenant's audit log entries with optional filtering."""
        input_serializer = AuditLogV2ListInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        fields = validate_fields_parameter(request.query_params.get("fields", "").replace("\x00", ""))

        queryset = self._apply_filters(self.get_queryset(), validated)

        page = self.paginate_queryset(queryset)
        serializer = AuditLogV2OutputSerializer(page, many=True, context={"request": request, "fields": fields})
        return self.get_paginated_response(serializer.data)

    @staticmethod
    def _apply_filters(queryset, validated):
        """Apply the validated list query parameters to the queryset."""
        principal_username = validated.get("principal_username")
        if principal_username:
            queryset = v2_name_filter(queryset, principal_username, field="principal_username")

        resource_type = validated.get("resource_type")
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        resource_id = validated.get("resource_id")
        if resource_id:
            queryset = queryset.filter(resource_uuid=resource_id)

        action = validated.get("action")
        if action:
            queryset = queryset.filter(action=action)

        created_after = validated.get("created_after")
        if created_after:
            queryset = queryset.filter(created__gte=created_after)

        created_before = validated.get("created_before")
        if created_before:
            queryset = queryset.filter(created__lte=created_before)

        return queryset
