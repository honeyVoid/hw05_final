from django.core.paginator import Paginator
from django.conf import settings


def pages_paginator(post, request):
    '''Dispalays last 10 newest posts.'''
    paginator = Paginator(post, settings.MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
