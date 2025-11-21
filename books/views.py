from .models import Book, Tag, CollectRecord
from django.shortcuts import render, get_object_or_404, redirect
import random
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import os
from django.http import FileResponse


# Create your views here.
def detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    recbooks = Book.objects.order_by('-upload_time')[:5]

    if request.user.is_authenticated:
        is_collected = CollectRecord.objects.filter(user=request.user, book=book).exists()  # 是否收藏
    else:
        is_collected = False

    return render(request, 'books/detail.html', {'book': book, 'recbooks': recbooks, 'is_collected': is_collected})


# 为

def read(request, book_id):
    if not request.user.is_authenticated:
        return render(request, 'no-permission.html')

    book = Book.objects.get(id=book_id)
    file_name = book.file.name.lower()

    if file_name.endswith('.pdf'):
        file_type = 'pdf'
    elif file_name.endswith('.epub'):
        file_type = 'epub'
    else:
        file_type = 'unknown'

    return render(request, 'books/read.html', {'book': book, 'file_type': file_type})


def search(request):
    # 获取所有标签
    tags = list(Tag.objects.all())

    # 随机取 5 个（如果标签不足 5 个，就取全部）
    random_tags = random.sample(tags, min(len(tags), 5))

    return render(request, 'books/search.html', {'tags': random_tags})


def search_view(request):
    query = request.GET.get('q', '')  # 获取搜索关键词
    results = []

    if query:
        results = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(uploader__first_name__icontains=query) |
            Q(uploader__last_name__icontains=query)
        ).distinct()  # distinct() 避免多标签导致的重复结果

    paginator = Paginator(results, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/search_view.html', {
        'query': query,
        'page_obj': page_obj,  # 分页对象
    })


def tag_books_view(request, tag_id):
    # 获取标签对象（如果不存在则返回 404）
    tag = get_object_or_404(Tag, id=tag_id)

    # 获取该标签下的所有书籍
    books = Book.objects.filter(tags=tag).order_by('-upload_time')

    # 分页（每页 8 本）
    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 渲染模板
    return render(request, 'books/tag.html', {
        'tag': tag,
        'page_obj': page_obj,
    })


# 收藏书
@login_required
def add_to_bookshelf(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user = request.user
    # 检查是否已经收藏过
    record = CollectRecord.objects.filter(user=user, book=book).first()
    if record:
        # 已收藏 -> 删除收藏
        record.delete()
    else:
        # 未收藏 -> 添加收藏
        CollectRecord.objects.create(user=user, book=book)

    return redirect('books_detail', book_id=book_id)


# 个人书架
@login_required
def bookshelf(request):
    user = request.user
    collect_records = CollectRecord.objects.filter(user=user).select_related('book')
    books = [record.book for record in collect_records]

    # 分页，每页 8 本书
    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')  # 获取 ?page= 参数
    page_obj = paginator.get_page(page_number)  # 自动处理无效页码

    return render(request, 'books/bookshelf.html', {'page_obj': page_obj})
