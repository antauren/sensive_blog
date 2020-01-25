from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Prefetch


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": len(Comment.objects.filter(post=post)),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(Post.objects.filter(tags=tag)),
    }


def serialize_post_optimized(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag_optimized(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count
    }


def index(request):
    tags_popular = Tag.objects.popular()

    posts = Post.objects \
        .prefetch_related('author') \
        .prefetch_related(Prefetch('tags', queryset=tags_popular))

    most_popular_posts = posts.popular()[:5] \
        .fetch_with_comments_count()

    most_fresh_posts = posts.all().order_by('-published_at')[:5] \
        .fetch_with_comments_count()

    most_popular_tags = tags_popular[:5]

    context = {
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts_popular = Post.objects.popular()

    post = posts_popular.get(slug=slug)

    comments = Comment.objects.filter(post=post).prefetch_related('author')

    serialized_comments = [{'text': comment.text,
                            'published_at': comment.published_at,
                            'author': comment.author.username,
                            }
                           for comment in comments]

    likes = post.likes.all()

    related_tags = post.tags.popular()  # all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': len(likes),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag_optimized(tag) for tag in related_tags],
    }

    tags_popular = Tag.objects.popular()

    most_popular_tags = tags_popular[:5]

    most_popular_posts = posts_popular[:5] \
        .prefetch_related('author') \
        .prefetch_related(Prefetch('tags', queryset=tags_popular)) \
        .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tags_popular = Tag.objects.popular()
    tag = tags_popular.get(title=tag_title)

    prefetch_tags = Prefetch('tags', queryset=tags_popular)

    most_popular_posts = Post.objects.popular()[:5] \
        .prefetch_related('author') \
        .prefetch_related(prefetch_tags) \
        .fetch_with_comments_count()

    related_posts = tag.posts.popular()[:20] \
        .prefetch_related('author') \
        .prefetch_related(prefetch_tags) \
        .fetch_with_comments_count()

    most_popular_tags = tags_popular[:5]

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        "posts": [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
