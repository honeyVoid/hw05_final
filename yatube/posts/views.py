from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


from posts.models import Post, Group, User, Follow
from posts.forms import PostForm, CommentForm
from posts.utils import pages_paginator


def index(request):
    '''Shows main page and last 10 posts.'''
    post_list = Post.objects.all()
    context = {
        'page_obj': pages_paginator(post_list, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''Shows last 10 group's posts.'''
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': pages_paginator(posts, request),
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    '''Shows user's profile and his last 10 posts.'''
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'post_count': post_count,
        'author': author,
        'page_obj': pages_paginator(post_list, request),
        'following': following

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''Shows post's details.'''
    post_detail = get_object_or_404(Post, pk=post_id)
    count = post_detail.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post_detail.comments.all()
    context = {
        'post_detail': post_detail,
        'count': count,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Allows user to create post if logget in.'''
    form = PostForm(request.POST, files=request.FILES or None)
    if request.method != 'POST' or not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    data = form.save(commit=False)
    data.author = request.user
    data.save()
    return redirect('posts:profile', data.author)


@login_required
def post_edit(request, post_id):
    '''Allows user to change post if user is author.'''
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None)
    if request.method != 'POST':
        context = {
            'form': form,
            'post_id': post_id,
            'is_edit': True,
        }
        return render(request, 'posts/create_post.html', context)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': pages_paginator(posts, request),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    obj = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if obj.exists():
        obj.delete()
    return redirect('posts:follow_index')
