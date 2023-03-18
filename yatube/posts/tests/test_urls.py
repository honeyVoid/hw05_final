from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class TestPostsUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='abobus')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='tets description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test text',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(TestPostsUrls.user)

    def test_posts_public_urls_is_accsesible(self):
        url_names = (
            '/',
            '/group/test-slug/',
            '/profile/abobus/',
            '/posts/1/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_posts_urls(self):
        url_names = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/profile/abobobus/follow/':
            '/auth/login/?next=/profile/abobobus/follow/'
        }
        for url, status in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, status)

    def test_get_not_exist_url(self):
        response = self.guest_client.get('/ddwedw/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_page_use_correct_teplate(self):
        url_template = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/abobus/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for url, template in url_template.items():
            with self.subTest(template=template):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
