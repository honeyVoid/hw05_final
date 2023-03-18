from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text='Тестовый пост',
        )

    def test_model_have_correct_object_names(self):
        value = str(PostModelTest.post)
        expected = PostModelTest.post.text[:15]
        self.assertEqual(value, expected)

    def test_post_verbose_name(self):
        task = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст.',
            'pub_date': 'Дата публикации.',
            'author': 'Автор.',
            'group': 'Группа.',
        }
        for field, value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, value)

    def test_post_help_text(self):
        task = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст.',
            'pub_date': 'Дата устанавливается автоматически.',
            'author': 'Автор указывактся автоматически',
            'group': 'Указывает к какой группе пренадлежит пост.',
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_have_correct_object_names(self):
        value = str(GroupModelTest.group)
        expected = GroupModelTest.group.title
        self.assertEqual(value, expected)

    def test_group_help_text(self):
        task = GroupModelTest.group
        field_help_text = {
            'title': 'Название группы.',
            'slug': 'Имя ссылки.',
            'description': 'Описание Группы',
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, value
                )

    def tets_group_verbose_name(self):
        task = GroupModelTest.group
        verbose_name_fields = {
            'title': 'Название группы.',
            'slug': 'Ссылка.',
            'description': 'Описание'
        }
        for field, value in verbose_name_fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, value
                )
