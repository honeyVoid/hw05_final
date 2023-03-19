import tempfile
import shutil

from django import forms
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='abobus')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
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
            content=TestPostViews.img,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=TestPostViews.user,
            text='test text',
            group=TestPostViews.group,
            image=TestPostViews.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(TestPostViews.user)

    def test_page_uses_correct_template(self):
        pages_name_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list', kwargs={'slug': TestPostViews.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': TestPostViews.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': TestPostViews.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': TestPostViews.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for reverse_name, template in pages_name_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        pages_list = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPostViews.group.slug}
            ),
            reverse('posts:profile', args=(TestPostViews.post.author,))
        )
        for page_objects in pages_list:
            with self.subTest(page_objects=page_objects):
                response = self.guest_client.get(page_objects)
                self.check_post(response.context['page_obj'][0])

    def test_post_detail_shows_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': TestPostViews.post.id})
        )

        self.check_post(response.context.get('post_detail'))

    def test_create_edit_shows_correct_context(self):
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, expected)

    def tets_create_post_shows_corect_contex(self):
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, expacted in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, expacted)

    def tets_check_group_post_in_index_page(self):
        response = self.auth_client.get(reverse('posts:index'))
        form_field = response.context['page_obj']
        expected = TestPostViews.post.get(group=TestPostViews.post.group)
        self.assertIn(expected, form_field)

    def test_check_group_post_in_group_page(self):
        response = self.auth_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': TestPostViews.group.slug})
        )
        form_field = response.context['page_obj']
        expected = Post.objects.get(group=self.post.group)
        self.assertIn(expected, form_field)

    def test_check_group_post_in_profile_page(self):
        response = self.auth_client.get(
            reverse('posts:profile',
                    kwargs={'username': TestPostViews.post.author})
        )
        form_field = response.context['page_obj']
        expected = Post.objects.get(group=self.post.group)
        self.assertIn(expected, form_field)

    def test_chech_post_not_in_other_group(self):
        response = self.auth_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': TestPostViews.group.slug}
            )
        )
        form_field = response.context['page_obj']
        expected = Post.objects.exclude(group=self.post.group)
        self.assertNotIn(expected, form_field)

    def test_comment(self):
        comment_vol = Comment.objects.count()
        form_data = {'text': 'test comment'}
        redirect = reverse('posts:post_detail', args=(TestPostViews.post.id, ))
        response = self.auth_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': TestPostViews.post.id},
            ), data=form_data, follow=True
        )
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(), comment_vol + 1)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'],
            author=TestPostViews.post.author,
        ).exists())

    def test_cache(self):
        response_1 = self.guest_client.get(
            reverse('posts:index')
        )
        cache_1 = response_1.content
        Post.objects.get(pk=1).delete()
        response_2 = self.guest_client.get(
            reverse('posts:index')
        )
        cache_2 = response_2.content
        self.assertEqual(cache_1, cache_2)

    def test_follow_index(self):
        response = self.auth_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
        Follow.objects.get_or_create(
            user=TestPostViews.user,
            author=TestPostViews.post.author
        )
        response_2 = self.auth_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_2.context['page_obj']), 1)
        self.assertIn(TestPostViews.post, response_2.context['page_obj'])
        self.check_post(response_2.context['page_obj'][0])

        another_user = User.objects.create(username='abobus2')
        self.auth_client.force_login(another_user)
        response_3 = self.auth_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_3.context['page_obj']), 0)

    def test_unfollow(self):
        Follow.objects.get_or_create(
            user=TestPostViews.user,
            author=TestPostViews.post.author
        )
        response = self.auth_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        Follow.objects.all().delete()
        response_2 = self.auth_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_2.context['page_obj']), 0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_in_pages(self):
        pages_list = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                args=(self.group.slug,)
            ),
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        for page in pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.check_post(response.context['page_obj'][0])

    def test_image_in_post_detail(self):
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.id,)
            )
        )
        self.check_post(response.context.get('post_detail'))

    def check_post(self, post):
        self.assertEqual(post.text, TestPostViews.post.text)
        self.assertEqual(post.author, TestPostViews.post.author)
        self.assertEqual(post.group, TestPostViews.post.group)
        self.assertEqual(post.image, TestPostViews.post.image)


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='honey')
        cls.group = Group.objects.create(
            title='test title',
            slug='test-slug',
            description='tets description'
        )
        cls.post = []
        for i in range(15):
            cls.post.append(Post(
                text=f'tets text № {i}',
                author=cls.author,
                group=cls.group
            ))
        Post.objects.bulk_create(TestPaginator.post)

    def setUp(self):
        self.guest_client = Client()

    def tets_firt_page(self):
        pages_list = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': TestPaginator.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': TestPaginator.author.username}
            )
        )
        for page in pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), settings.MAX_POSTS
                )

    def test_second_page_contains_three_records(self):
        pages_list = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': TestPaginator.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': TestPaginator.author.username}
            )
        )
        for page in pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page + '?page=2')
                count = len(TestPaginator.post)
                self.assertEqual(
                    len(response.context['page_obj']),
                    count - settings.MAX_POSTS
                )


class TetsFollow(TestCase):
    def setUp(self) -> None:
        self.auth_client = Client()
        self.auth_client_2 = Client()
        self.follower = User.objects.create(username='abobus1')
        self.following = User.objects.create(username='abobus2')
        self.auth_client.force_login(self.follower)
        self.auth_client_2.force_login(self.following)
        self.post = Post.objects.create(
            author=self.following,
            text='tets text'
        )

    def test_follow_index(self):
        self.auth_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.following,)
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)
        self.assertTrue(
            Follow.objects.filter(user=TestPostViews.user).exists()
        )

    def test_unfollow_index(self):
        self.auth_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.following,)
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)
