from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.auth import get_user
from django.core import mail
from allauth.account.views import LoginView, SignupView

import pytest
from pytest_django.asserts import assertTemplateUsed, assertFormError, assertRedirects, assertContains

from users.views import CustomLogoutView


################## Fixture Factories ##################
@pytest.fixture
def user_factory(db):
    def create_user(user_id,
                    first_name="name",
                    last_name="name",
                    phone_number="01223334455",
                    password="test123456789"):
        user = get_user_model().objects.create_user(user_id=user_id,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    phone_number=phone_number,
                                                    password=password,
                                                    user_type="T")
        return user

    return create_user


################## Fixtures ##################
@pytest.fixture
def user_1(db, user_factory):
    return user_factory("test_user")


################## Test URL ##################
def test_signup_url(client, db):
    url = reverse("account_signup")
    assert url == "/accounts/signup/"
    assert resolve(url).func.__name__ == SignupView.__name__
    response = client.get(url)
    assertTemplateUsed(response, "account/signup.html")


def test_login_url(client, db):
    url = reverse("account_login")
    assert url == "/accounts/login/"
    assert resolve(url).func.__name__ == LoginView.__name__
    response = client.get(url)
    assertTemplateUsed(response, "account/login.html")


def test_logout_url(client, user_1):
    client.force_login(user_1)
    url = reverse("logout")
    assert url == "/users/logout/"
    assert resolve(url).func.__name__ == CustomLogoutView.__name__
    response = client.get(url)
    assertTemplateUsed(response, "account/logout.html")


def test_mail_url(client, user_1):
    client.force_login(user_1)

    url = reverse("account_email")
    assert url == "/accounts/email/"

    response = client.get(url)
    assertTemplateUsed(response, "account/email.html")
    assertContains(response, "DjS")


################## Test App ##################
def test_signup_successful(client, db):
    url = reverse("account_signup")
    data = {
        "first_name": "test_firstname",
        "last_name": "test_last_name",
        "user_type": "SS",
        "username": "test_user",
        "password1": "test123456",
        "password2": "test123456",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert get_user(client).is_authenticated
    # TODO: IF YOU MOVED create-school TO USERS, THEN CHANGE THIS
    assertRedirects(response, reverse("supports:create-school"))


def test_signup_unsuccessful(client, db):
    url = reverse("account_signup")
    # Username, which is required, isn't included here.
    data = {
        "first_name": "test_firstname",
        "last_name": "test_last_name",
        "user_type": "SS",
        "password1": "test123456",
        "password2": "test123456",
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert not get_user(client).is_authenticated
    assertTemplateUsed(response, "account/signup.html")
    assertFormError(response, "form", "username", "This field is required.")


def test_login_successful(client, user_1):
    url = reverse("account_login")
    data = {
        "login": "test_user",
        "password": "test123456789",
    }
    response = client.post(url, data)
    messages = [*get_messages(response.wsgi_request)]
    assert get_user(client).is_authenticated
    assert str(
        messages[-1]
    ) == f"Successfully signed in as {get_user(client).get_username()}."
    assert response.status_code == 302
    assertRedirects(response, reverse("home:home"))


def test_login_unsuccessful(client, user_1):
    url = reverse("account_login")
    data = {
        "login": "invalid_id",
        "password": "test123456789",
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert not get_user(client).is_authenticated
    assertTemplateUsed(response, "account/login.html")
    assertFormError(
        response, "form", None,
        "The username and/or password you specified are not correct.")
