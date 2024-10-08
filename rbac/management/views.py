#
# Copyright 2019 Red Hat, Inc.
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

"""API views for import organization"""
# flake8: noqa
# pylint: disable=unused-import
from management.principal.view import PrincipalView
from management.group.view import GroupViewSet
from management.role.view import RoleViewSet
from management.access.view import AccessView
from management.permission.view import PermissionViewSet
from management.audit_log.view import AuditLogViewSet
from management.workspace.view import WorkspaceViewSet
