from django.shortcuts import render, redirect, get_object_or_404
from books.models import Book, Tag
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden  # [新增] 导入 JsonResponse
from django.urls import reverse
from django.db import transaction  # 导入事务，确保数据一致性
from .forms import BookForm


def index(request):
    books = Book.objects.all().order_by('-upload_time')
    paginator = Paginator(books, 8)  # 每页显示 5 条数据

    page_number = request.GET.get('page')  # 获取页码参数
    page_obj = paginator.get_page(page_number)  # 获取当前页对象

    return render(request, 'index.html', {'page_obj': page_obj})
    # return render(request, 'index.html', {'books': books})


def test(request):
    return render(request, 'test.html')


def portfolio(request):
    return render(request, 'portfolio.html')


def myadmin(request):
    user = request.user

    if not request.user.is_authenticated:
        return render(request, 'no-permission.html')

    if user.is_superuser:
        # 2. 如果是超级管理员，获取所有书本
        books = Book.objects.all().order_by('-upload_time')
    else:
        # 3. 如果只是普通 staff，只获取自己上传的 (uploader=user)
        books = Book.objects.filter(uploader=user).order_by('-upload_time')

    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')  # 获取页码参数
    page_obj = paginator.get_page(page_number)  # 获取当前页对象

    return render(request, 'admin/admin_book.html', {'page_obj': page_obj})


@login_required
def admin_book_add(request):
    """
    视图2: 添加书本页 (已支持 AJAX 进度条)
    """

    # [新增] 检查这个请求是否是 AJAX 请求
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, 'no-permission.html')

    if request.method == 'POST':
        # 1. 从 request.POST 获取文本数据
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description', '')
        tags_string = request.POST.get('tags')

        # 2. 从 request.FILES 获取文件数据
        cover_image = request.FILES.get('cover')
        book_file = request.FILES.get('book_file')

        # 3. 数据校验
        if not all([title, author, cover_image, book_file]):
            err_msg = 'Required fields are missing'  # [修改] 存为变量
            print(err_msg)

            if is_ajax:  # [新增] 如果是 AJAX，返回 JSON 错误
                return JsonResponse({'error': err_msg}, status=400)
            else:  # [修改] 保留旧的 render 逻辑
                return render(request, 'admin/admin_book_add.html', {'err': err_msg})

        # 4. 创建并保存 Book 实例
        try:
            new_book = Book(
                title=title,
                author=author,
                description=description,
                cover=cover_image,
                file=book_file,
                uploader=request.user
            )
            new_book.save()

            # --- 5. 处理 Tags ---
            if tags_string:
                tag_names = tags_string.split(',')
                for tag_name in tag_names:
                    name = tag_name.strip()
                    if name:
                        tag_obj, created = Tag.objects.get_or_create(name=name)
                        new_book.tags.add(tag_obj)

            # 6. 操作成功
            if is_ajax:  # [新增] 如果是 AJAX，返回 JSON 成功信息
                # [新增] 告诉前端下一步要跳转到哪里
                redirect_url = reverse('admin_book')  # 使用你自己的 URL name
                return JsonResponse({'success': True, 'redirect_url': redirect_url})
            else:  # [修改] 保留旧的重定向逻辑
                return redirect('admin_book')

        except Exception as e:
            err_msg = f'Upload fail: {e}'  # [修改] 存为变量
            print(e)

            if is_ajax:  # [新增] 如果是 AJAX，返回 JSON 错误
                return JsonResponse({'error': err_msg}, status=500)  # 500 服务器错误
            else:  # [修改] 保留旧的 render 逻辑
                return render(request, 'admin/admin_book_add.html', {'err': err_msg})

    # GET 请求
    return render(request, 'admin/admin_book_add.html', {'form_title': '添加新书'})


@login_required
def admin_book_delete(request, book_id):
    print("start delete")
    """
    视图: 删除书本
    - 只接受 POST 请求
    - 检查用户权限
    """
    # 1. 根据 URL 传来的 book_id 获取书本对象
    book = get_object_or_404(Book, pk=book_id)

    # 2. [关键] 权限检查
    # 检查当前登录的用户是否是超级用户 (admin)
    # 或者 检查当前用户是否是这本书的上传者
    # [正面检查] 检查谁 "允许" 删除
    is_allowed = False

    if request.user.is_superuser:
        is_allowed = True
    elif request.user.is_staff and book.uploader == request.user:
        is_allowed = True

    # 如果不允许
    if not is_allowed:
        return render(request, 'no-permission.html')

    # 3. 如果权限检查通过，执行删除
    try:
        # book.delete() 会自动处理数据库中的删除
        # 注意：Django 默认*不会*删除 S3 或其他云存储上的文件
        # 但它会删除你本地 'media/covers/' 和 'media/books/' 里的文件
        book.delete()

        # 4. 操作成功，重定向回书本列表页
        return redirect('admin_book')  # 假设你的书本列表页 URL name 是 'admin_book'

    except Exception as e:
        # (可选) 处理删除失败的异常
        # 比如可以重定向回列表页并带上一个错误消息
        return redirect('admin_book')  # 简单处理，还是跳回列表页


def admin_book_edit(request, book_id):


    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    book = get_object_or_404(Book, pk=book_id)

    is_allowed = False

    if request.user.is_superuser:
        is_allowed = True
    elif request.user.is_staff and book.uploader == request.user:
        is_allowed = True

    # 如果不允许
    if not is_allowed:
        return render(request, 'no-permission.html')

    if request.method == 'POST':
        # --- 3. 获取 POST 数据 ---
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description', '')
        tags_string = request.POST.get('tags')

        # 从 request.FILES 获取新文件（可能为空）
        new_cover_image = request.FILES.get('cover')
        new_book_file = request.FILES.get('book_file')

        if not all([title, author]):
            err_msg = 'Required fields are missing'  # [修改] 存为变量
            print(err_msg)

            if is_ajax:  # [新增] 如果是 AJAX，返回 JSON 错误
                return JsonResponse({'error': err_msg}, status=400)
            else:  # [修改] 保留旧的 render 逻辑
                return render(request, 'admin/admin_book_add.html', {'err': err_msg, 'book': book})

        # --- 4. 事务处理：保证数据一致性 ---
        try:
            with transaction.atomic():

                # --- 5. 更新文本字段 ---
                # 直接赋值，Django 会负责跟踪哪些字段变了
                book.title = title
                book.author = author
                book.description = description

                # --- 6. 核心：处理文件替换逻辑 ---
                # 当你对 FileField/ImageField 赋新值时，Django 会自动删除旧文件

                # A. 检查是否有新的封面上传
                if new_cover_image:
                    # 如果有旧文件，Django 默认会先删除旧文件，再保存新文件
                    book.cover.delete(save=False)
                    book.cover = new_cover_image
                # 注意：如果 new_cover_image 为 None，我们什么都不做，book.cover 保持不变

                # B. 检查是否有新的书本文件上传
                if new_book_file:
                    book.file.delete(save=False)
                    book.file = new_book_file

                # 7. 保存主对象 (更新数据库)
                book.save()

                # --- 8. 处理 Tags (多对多关系) ---
                # 更新 M2M 关系最简单的方法是先清空，再添加
                book.tags.clear()

                if tags_string:
                    tag_names = tags_string.split(',')
                    for tag_name in tag_names:
                        name = tag_name.strip()
                        if name:
                            tag_obj, created = Tag.objects.get_or_create(name=name)
                            book.tags.add(tag_obj)

            # 9. 操作成功，重定向到列表页或详情页
            if is_ajax:  # [新增] 如果是 AJAX，返回 JSON 成功信息
                # [新增] 告诉前端下一步要跳转到哪里
                redirect_url = reverse('admin_book')  # 使用你自己的 URL name
                return JsonResponse({'success': True, 'redirect_url': redirect_url})
            else:  # [修改] 保留旧的重定向逻辑
                return redirect('admin_book')

        except Exception as e:
            # 事务失败，文件和数据库操作都会回滚 (如果支持)
            return render(request, 'admin/admin_book_edit.html', {'book': book, 'err': f'更新失败: {e}'})

    # 准备 tags 字符串用于回显
    current_tags = ', '.join([tag.name for tag in book.tags.all()])
    return render(request, 'admin/admin_book_edit.html', {'current_tags': current_tags, 'book': book})
