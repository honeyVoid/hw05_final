from django.db import models
from django.contrib.auth import get_user_model


class Group(models.Model):
    '''Model for group creating'''
    title = models.CharField(
        max_length=200,
        help_text='Название группы.',
        verbose_name='Название группы.'
    )
    slug = models.SlugField(
        unique=True,
        help_text='Имя ссылки.',
        verbose_name='Ссылка.'
    )
    description = models.TextField(
        help_text='Описание Группы',
        verbose_name='Описание',
    )

    def __str__(self):
        return self.title


User = get_user_model()


class Post(models.Model):
    '''Model for posts creating.'''
    text = models.TextField(
        help_text='Введите текст.',
        verbose_name='Текст.'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации.',
        help_text='Дата устанавливается автоматически.'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор.',
        help_text='Автор указывактся автоматически',
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        help_text='Указывает к какой группе пренадлежит пост.',
        verbose_name='Группа.',
    )
    image = models.ImageField(
        help_text='картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        '''Shows first 15 characters of text.'''
        return self.text[:15]

    class Meta:
        '''Used for ordering posts by newest.'''
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='коментарий к запси',
        help_text='добавьте коментрай'
    )
    created = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True
    )

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='получатель',
        help_text='оставить коммент'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='отправитель',
        help_text='отправитель'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='уникальная связка'
            )
        ]
        # не понял как этим пользоваться от слова совсем

        def __str__(self):
            return (f'{self.user} подписан на {self.author}')
