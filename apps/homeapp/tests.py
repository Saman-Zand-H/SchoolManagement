import pytest
from pytest_django.asserts import (assertRedirects, assertContains, assertNotContains,
                                   assertTemplateUsed, assertTemplateNotUsed)
from django.contrib.auth import get_user_model, get_user
from django.urls import reverse_lazy, resolve, reverse
from django.contrib.messages import get_messages

from mainapp.models import Article
from homeapp.views import AddArticleView, ArticleDetailView, ArticlesTemplateView
from supports.models import School


# ========= Fixture Factories =========
@pytest.fixture
def user_factory(db):
    def create_user(username,
                    first_name="name",
                    last_name="name",
                    password="test123456789"):
        user = get_user_model().objects.create_user(username=username,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    password=password,
                                                    email=None,
                                                    user_type="SS")
        return user

    return create_user

# ========= Fixtures =========
@pytest.fixture
def support_1(db, user_factory):
    return user_factory("support_test1")


@pytest.fixture
def school_1(db, support_1):
    return School.objects.create(
        name="Test School 1", support=support_1)


# ========= Tests =========
def test_create_article_successful(client, school_1):
    client.force_login(school_1.support)
    
    assert Article.objects.count() == 0
    url = reverse_lazy("home:add-article")
    assert url == "/articles/add/"
    assert resolve(url).func.__name__ == AddArticleView.__name__
    
    data = {
        "title": "Test Article",
        "categories": "test, test2, test3",
        "text": "This is a test article.",
    }    
    response = client.post(url, data=data)
    messages = [*get_messages(response.wsgi_request)]
    
    assert response.status_code == 302
    assert str(messages[-1]) == "Article saved successfully."
    assert Article.objects.count() == 1
    last_article = Article.objects.last()
    assertRedirects(
        response, reverse("home:article-detail", 
                          kwargs={"pk": last_article.pk}))
    assert last_article.author == get_user(client)
    

def test_create_article_unsuccessful(client, school_1):
    client.force_login(school_1.support)
    
    assert Article.objects.count() == 0
    url = reverse_lazy("home:add-article")
    
    data = { 
        "categories": "test. test2",      
        "text": "This is a test article.",
    }
    response = client.post(url, data=data)
    messages = [*get_messages(response.wsgi_request)]
    
    assert response.status_code == 302
    assertRedirects(response, reverse("home:articles"))
    assert str(messages[-1]) == "Provided inputs are invalid."
    assert Article.objects.count() == 0
    

def test_articles_template_view(client, school_1):
    client.force_login(school_1.support)
    
    assert Article.objects.count() == 0
    url = reverse_lazy("home:articles")
    assert url == "/articles/"
    assert resolve(url).func.__name__ == ArticlesTemplateView.__name__
    
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/articles.html")
    assertTemplateNotUsed(response, "dashboard/add_article.html")
    assertNotContains(response, "Test Article")
    assert "articles" in response.context["segment"]
    assert response.context["nav_color"] == "bg-gradient-info"
    
    Article.objects.create(
        title="Test Article",
        categories="test, test2, test3".split(", "),
        text="This is a test article.",
        author=get_user(client),
        school=school_1,
    )
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/articles.html")
    assertTemplateNotUsed(response, "dashboard/add_article.html")
    assert "articles" in response.context["segment"]
    assert response.context["nav_color"] == "bg-gradient-info"
    assertContains(response, "Test Article")


def test_article_detail_view(client, school_1):
    client.force_login(school_1.support)
    
    assert Article.objects.count() == 0
    url = reverse("home:article-detail", kwargs={"pk": 1})
    assert resolve(url).func.__name__ == ArticleDetailView.__name__
    
    response = client.get(url)
    assert response.status_code == 404
    
    article = Article.objects.create(
        title="Test Article",
        categories="test, test2, test3".split(", "),
        text="This is a test article.",
        author=get_user(client),
        school=school_1,
    )
    url = reverse("home:article-detail", kwargs={"pk": article.pk})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "dashboard/article_detail.html")
    assertTemplateNotUsed(response, "dashboard/add_article.html")
    assert "articles" in response.context["segment"]
    assert response.context["nav_color"] == "bg-gradient-info"
    assertContains(response, "Test Article")
    assertContains(response, "This is a test article.")
