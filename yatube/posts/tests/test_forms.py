from http import HTTPStatus as status
import tempfile

from django.urls import reverse
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Post, Group, Comment


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestForms(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='abobus')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description'
        )
        cls.img = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=TestForms.img,
            content_type='image/gif'
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(TestForms.user)

    def test_post_created(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'test text',
            'group': TestForms.group.id,
            'image': self.uploaded

        }
        response = self.auth_client.post(
            reverse('posts:post_create'), data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': TestForms.user.username}
            )
        )
        self.assertTrue(
            Post.objects.filter(text=form_data['text'], author=TestForms.user,
                                group=TestForms.group.id,
                                image='posts/small.gif').exists())
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertEqual(response.status_code, status.OK)

    def test_post_editing(self):
        new_image = SimpleUploadedFile(
            name='new_small.gif',
            content=TestForms.img,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=self.user,
            text='tets text',
        )
        count_posts = Post.objects.count()
        form_data = {
            'text': 'editing text',
            'group': TestForms.group.id,
            'image': new_image
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', args=(post.id,)),
            data=form_data,
            follow=True,
        )
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        )
        self.assertRedirects(response, redirect)
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertTrue(
            Post.objects.filter(text=form_data['text'], author=TestForms.user,
                                group=TestForms.group.id,
                                image='posts/new_small.gif').exists())


class TestComment(TestCase):
    def setUp(self):
        self.client_auth_following = Client()
        self.user_following = User.objects.create_user(username='abobus2')
        self.client_auth_following.force_login(self.user_following)
        self.author = User.objects.create_user(username='abobus1')
        self.post = Post.objects.create(
            author=self.author,
            text='test text'
        )

    def test_add_comment(self):
        form_data = {'text': 'tests comm'}
        self.client_auth_following.post(
            reverse(
                'posts:add_comment',
                args=(self.post.id,)
            ), data=form_data, follow=True
        )
        response = self.client_auth_following.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertContains(response, form_data['text'])
        self.assertTrue(
            Comment.objects.filter(
                author=self.user_following,
                text=form_data['text'],
                post=self.post
            ).exists()
        )
