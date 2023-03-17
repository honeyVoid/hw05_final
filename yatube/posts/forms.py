from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def check_text_field(value):
        data = value.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Это поле обязательно для заполнения')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
