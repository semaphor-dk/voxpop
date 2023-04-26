from datetime import timedelta

import pytest as pytest
from django.urls import reverse
from django.utils import timezone

from voxpop.models import Organisation
from voxpop.models import Voxpop


@pytest.mark.django_db
@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="test",
        password="test",
    )


@pytest.mark.django_db
@pytest.fixture
def organisation():
    return Organisation.objects.create(
        name="Test Organisation",
    )


@pytest.mark.django_db
@pytest.fixture
def voxpop(organisation):
    now = timezone.now()
    start_at = now
    expires_at = now + timedelta(hours=2)
    return Voxpop.objects.create(
        organisation=organisation,
        title="Test Voxpop",
        description="Test Description",
        created_by="foobar",
        starts_at=start_at,
        expires_at=expires_at,
    )


@pytest.mark.django_db
def test_api_voxpops_list(client, voxpop):
    url = reverse("voxpop:api-1.0.0:voxpops")
    response = client.get(url)
    assert response.status_code == 200
    starts_at = voxpop.starts_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[0:-3] + "Z"
    expires_at = voxpop.expires_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[0:-3] + "Z"
    assert response.json() == [
        {
            "id": 1,
            "organisation": voxpop.organisation.id,
            "title": "Test Voxpop",
            "description": "Test Description",
            "created_by": "foobar",
            "starts_at": starts_at,
            "expires_at": expires_at,
            "is_moderated": True,
            "allow_anonymous": False,
            "question_count": 0,
        },
    ]
