from django.shortcuts import render, redirect, get_object_or_404
from books.models import Book, Tag
from login.models import User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponseForbidden  # [新增] 导入 JsonResponse
from django.urls import reverse
from django.db import transaction  # 导入事务，确保数据一致性
from django.db.models import Q  # 用于搜索
from .forms import BookForm, UserEditForm


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

    # 排序
    sort_by = request.GET.get('sort', '-upload_time')
    allowed_sort_fields = ['upload_time', '-upload_time', 'title', '-title', 'author', '-author']
    if sort_by not in allowed_sort_fields:
        sort_by = '-upload_time'

    if not request.user.is_authenticated:
        return render(request, 'no-permission.html')

    if user.is_superuser:
        # 2. 如果是超级管理员，获取所有书本
        books = Book.objects.all().order_by(sort_by)
    else:
        # 3. 如果只是普通 staff，只获取自己上传的 (uploader=user)
        books = Book.objects.filter(uploader=user).order_by('-upload_time')

    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')  # 获取页码参数
    page_obj = paginator.get_page(page_number)  # 获取当前页对象

    return render(request, 'admin/admin_book.html', {'page_obj': page_obj, 'sort_by': sort_by})


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
    next_url = request.META.get('HTTP_REFERER', '/')
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
        return redirect(next_url)  # 假设你的书本列表页 URL name 是 'admin_book'

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


def admin_tag(request):
    sort_by = request.GET.get('sort', 'id')
    allowed_sort_fields = ['id', '-id', 'name', '-name']
    if sort_by not in allowed_sort_fields:
        sort_by = 'id'

    if not request.user.is_superuser and not request.user.is_staff:
        return render(request, 'no-permission.html')

    tags = Tag.objects.all().order_by(sort_by)
    paginator = Paginator(tags, 8)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'admin/admin_tag.html', {'page_obj': page_obj, 'sort_by': sort_by})


def admin_tag_add(request):
    next_url = request.META.get('HTTP_REFERER', '/')

    if not request.user.is_superuser and not request.user.is_staff:
        return render(request, 'no-permission.html')

    if request.method == 'POST':
        name = request.POST.get('name', "").strip()
        if name:
            Tag.objects.get_or_create(name=name)
    return redirect(next_url)


def admin_tag_delete(request):
    next_url = request.META.get('HTTP_REFERER', '/')
    if not request.user.is_superuser and not request.user.is_staff:
        return render(request, 'no-permission.html')

    if request.method == 'POST':
        print("start to delete tag")
        tag_id = request.POST.get('id', "").strip()
        if tag_id:
            tag_to_delete = get_object_or_404(Tag, id=tag_id)
            tag_to_delete.delete()
            print("delete tag")
    return redirect(next_url)


def admin_tag_edit(request):
    next_url = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        # 2. 获取用户提交的新名字
        new_name = request.POST.get("name", "").strip()
        tagid = request.POST.get("id", "").strip()

        tag = get_object_or_404(Tag, id=tagid)

        if new_name:
            # 可选：检查新名字是否和其他标签重复 (虽然 unique=True 在数据库层面会报错，但提前检查用户体验更好)
            if Tag.objects.filter(name=new_name).exclude(id=tagid).exists():
                # 这里可以添加一个错误消息传递给前端
                print("该标签名已存在")
                # return render(...)
            else:
                # 3. 更新并保存
                tag.name = new_name
                tag.save()
    return redirect(next_url)  # 更新成功，跳回列表页


def admin_user(request):
    if not request.user.is_superuser:
        return render(request, 'no-permission.html')
    """用户列表视图"""
    query = request.GET.get('q')
    if query:
        # 实现简单的搜索功能
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).order_by('id')
    else:
        users = User.objects.all().order_by('id')

    paginator = Paginator(users, 8)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    form = UserEditForm()
    context = {'form': form,'page_obj': page_obj, 'query': query}
    return render(request, 'admin/admin_user.html', context)


@permission_required('is_superuser', raise_exception=True)
def admin_user_active(request):
    """激活/禁用用户（POST请求）"""
    if request.method == 'POST':
        user_id = request.POST.get('id')
        user = get_object_or_404(User, pk=user_id)
        user.is_active = not user.is_active
        user.save()
    # 操作完成后返回用户列表或详情页
    return redirect('admin_user')


@permission_required('is_superuser', raise_exception=True)
def admin_user_edit(request):
    """
    用户编辑视图：通过隐藏字段中的 ID 来处理用户
    """
    if request.method == 'POST':
        # 1. POST 请求：从表单中获取隐藏的 user_id
        user_id = request.POST.get('user_id')
        print("修改用户信息，user id:",user_id)
        if not user_id:
            # 如果没有 ID，则返回错误或重定向
            # 实际应用中需要更好的错误处理
            return redirect('admin_user')

        user = get_object_or_404(User, pk=user_id)

        # 2. 绑定表单数据和用户实例
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            # 3. 数据验证成功：保存表单
            form.save()
            return redirect('admin_user')

        # 如果表单验证失败，需要重新渲染表单（并传递 user 实例）
        # ⚠️ 注意：如果表单验证失败，需要确保 form 和 user 实例被正确传递到渲染逻辑

    else:
        # 4. GET 请求：此视图现在不能直接用于显示空白表单，
        # 因为我们不知道要编辑哪个用户。
        #
        # 如果是 GET 请求，通常应该重定向回用户列表，或者
        # 要求 URL 中有查询参数，例如 ?user_id=123
        user_id = request.GET.get('user_id')
        if not user_id:
            return redirect('admin_user') # 如果没有ID，返回列表

        user = get_object_or_404(User, pk=user_id)
        form = UserEditForm(instance=user)

    print("check",form)
    context = {
        'form': form,
        'user_id': user.pk, # 用于隐藏字段
        'last_login_time': user.last_login if user.last_login else 'N/A'
    }

    # 渲染包含表单的模板
    return render(request, 'admin/admin_user.html', context)

def admin_core(request):
    if not request.user.is_superuser:
        return render(request, 'no-permission.html')
    return render(request, 'admin/admin_core.html')