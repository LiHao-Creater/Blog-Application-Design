from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import BlogPost

User = get_user_model()


class BlogSecurityTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345!")
        self.u2 = User.objects.create_user(username="u2", password="pass12345!")
        self.p1 = BlogPost.objects.create(owner=self.u1, title="t1", text="hello")

    def test_home_is_public(self):
        r = self.client.get(reverse("blogs:home"))
        self.assertEqual(r.status_code, 200)

    def test_detail_is_public(self):
        r = self.client.get(reverse("blogs:detail", args=[self.p1.pk]))
        self.assertEqual(r.status_code, 200)

    def test_create_requires_login(self):
        r = self.client.get(reverse("blogs:create"))
        self.assertEqual(r.status_code, 302)  # redirect to login

    def test_owner_can_edit(self):
        self.client.login(username="u1", password="pass12345!")
        r = self.client.get(reverse("blogs:edit", args=[self.p1.pk]))
        self.assertEqual(r.status_code, 200)

    def test_non_owner_cannot_edit(self):
        self.client.login(username="u2", password="pass12345!")
        r = self.client.get(reverse("blogs:edit", args=[self.p1.pk]))
        self.assertEqual(r.status_code, 404)  # get_queryset 限制后不可见

    def test_create_sets_owner(self):
        self.client.login(username="u1", password="pass12345!")
        r = self.client.post(reverse("blogs:create"), data={"title": "new", "text": "content"})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(BlogPost.objects.filter(title="new", owner=self.u1).exists())
