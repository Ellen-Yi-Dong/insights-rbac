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
"""Test the principal cleaner."""
import logging
import uuid

from unittest.mock import patch

from rest_framework import status

from management.group.model import Group
from management.principal.cleaner import clean_tenant_principals
from management.principal.model import Principal
from tests.identity_request import IdentityRequest


class PrincipalCleanerTests(IdentityRequest):
    """Test the principal cleaner functions."""

    def setUp(self):
        """Set up the principal cleaner tests."""
        super().setUp()
        self.group = Group(name="groupA", tenant=self.tenant)
        self.group.save()

    def test_principal_cleanup_none(self):
        """Test that we can run a principal clean up on a tenant with no principals."""
        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        self.assertEqual(Principal.objects.count(), 0)

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_200_OK, "data": []},
    )
    def test_principal_cleanup_skip_cross_account_principals(self, mock_request):
        """Test that principal clean up on a tenant will skip cross account principals."""
        Principal.objects.create(username="user1", tenant=self.tenant)
        Principal.objects.create(username="CAR", cross_account=True, tenant=self.tenant)
        self.assertEqual(Principal.objects.count(), 2)

        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        self.assertEqual(Principal.objects.count(), 1)

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_200_OK, "data": []},
    )
    def test_principal_cleanup_skips_service_account_principals(self, mock_request):
        """Test that principal clean up on a tenant will skip service account principals."""
        # Create a to-be-removed user principal and a service account that should be left untouched.
        service_account_client_id = str(uuid.uuid4())
        Principal.objects.create(username="regular user", tenant=self.tenant)
        Principal.objects.create(
            username=f"service-account-{service_account_client_id}",
            service_account_id=service_account_client_id,
            tenant=self.tenant,
            type="service-account",
        )
        self.assertEqual(Principal.objects.count(), 2)

        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")

        # Assert that the only principal left for the tenant is the service account, which should have been left
        # untouched.
        principals = Principal.objects.all()
        self.assertEqual(len(principals), 1)

        service_account = principals[0]
        self.assertEqual(service_account.service_account_id, service_account_client_id)
        self.assertEqual(service_account.type, "service-account")
        self.assertEqual(service_account.username, f"service-account-{service_account_client_id}")

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_200_OK, "data": []},
    )
    def test_principal_cleanup_principal_in_group(self, mock_request):
        """Test that we can run a principal clean up on a tenant with a principal in a group."""
        self.principal = Principal(username="user1", tenant=self.tenant)
        self.principal.save()
        self.group.principals.add(self.principal)
        self.group.save()
        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        # we are disabling the deletion so temporarily the principal will not be deleted
        self.assertEqual(Principal.objects.count(), 1)
        # self.assertEqual(Principal.objects.count(), 0)

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_200_OK, "data": []},
    )
    def test_principal_cleanup_principal_not_in_group(self, mock_request):
        """Test that we can run a principal clean up on a tenant with a principal not in a group."""
        self.principal = Principal(username="user1", tenant=self.tenant)
        self.principal.save()
        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        self.assertEqual(Principal.objects.count(), 0)

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_200_OK, "data": [{"username": "user1"}]},
    )
    def test_principal_cleanup_principal_exists(self, mock_request):
        """Test that we can run a principal clean up on a tenant with an existing principal."""
        self.principal = Principal(username="user1", tenant=self.tenant)
        self.principal.save()
        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        self.assertEqual(Principal.objects.count(), 1)

    @patch(
        "management.principal.proxy.PrincipalProxy._request_principals",
        return_value={"status_code": status.HTTP_504_GATEWAY_TIMEOUT},
    )
    def test_principal_cleanup_principal_error(self, mock_request):
        """Test that we can handle a principal clean up with an unexpected error from proxy."""
        self.principal = Principal(username="user1", tenant=self.tenant)
        self.principal.save()
        try:
            clean_tenant_principals(self.tenant)
        except Exception:
            self.fail(msg="clean_tenant_principals encountered an exception")
        self.assertEqual(Principal.objects.count(), 1)
