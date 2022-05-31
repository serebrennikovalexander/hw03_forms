from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

NUMBER_OF_POSTS = settings.NUMBER_OF_POSTS
NUMBER_OF_CHARACTERS = settings.NUMBER_OF_CHARACTERS


# Главная страница
def index(request):
    posts = Post.objects.select_related('author').all()
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    number_of_posts = author.posts.count()
    paginator = Paginator(author_posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'number_of_posts': number_of_posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = Post.objects.select_related('author', 'group').get(pk=post_id)
    number_of_posts = post.author.posts.count()
    title = post.text[:NUMBER_OF_CHARACTERS]
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'title': title,
        'number_of_posts': number_of_posts,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)

        return render(request, template, {'form': form})

    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    template = 'posts/create_post.html'
    post = Post.objects.select_related('author', 'group').get(pk=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post_id)

        form = PostForm(instance=post)
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit,
        }
        return render(request, template, context)

    return redirect('posts:post_detail', post_id)
