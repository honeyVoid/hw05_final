from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestStaticPageUrl(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exist(self):
        url_names = ('/about/author/', '/about/tech/')
        for url in url_names:
            with self.subTest(url=url):
                response_code = self.guest_client.get(url)
                self.assertEqual(response_code.status_code, HTTPStatus.OK)

    def test_url_uses_correct_html(self):
        url_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in url_templates.items():
            with self.subTest(url=url):
                response_html = self.guest_client.get(url)
                self.assertTemplateUsed(response_html, template)
