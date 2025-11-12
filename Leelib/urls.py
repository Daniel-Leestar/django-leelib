"""
URL configuration for Leelib project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('admin/', admin.site.urls, name='core_admin'),
    path('admin-book/', views.myadmin, name='admin_book'),
    path('admin-book-add/', views.admin_book_add, name='admin_book_add'),
    path('admin-book-delete/<int:book_id>/', views.admin_book_delete, name='admin_book_delete'),
    path('admin-book-edit/<int:book_id>/', views.admin_book_edit, name='admin_book_edit'),
    path('admin-tag/', views.admin_tag, name='admin_tag'),
    path('admin-tag-add/', views.admin_tag_add, name='admin_tag_add'),
    path('admin-tag-delete/', views.admin_tag_delete, name='admin_tag_delete'),
    path('admin-tag-edit/', views.admin_tag_edit, name='admin_tag_edit'),
    path('admin-user/', views.admin_user, name='admin_user'),
    path('admin-user-active/', views.admin_user_active, name='admin_user_active'),
    path('admin-user-edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-user-add/', views.admin_user_add, name='admin_user_add'),
    path('admin-user-delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-user-core/', views.admin_core, name='admin_core'),
    path('', include('login.urls')),
    path('', include('books.urls'))
]

if settings.DEBUG is False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # 这一行通常用于 DEBUG=True 时服务媒体文件
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # [新增] 仅在本地测试 DEBUG=False 时，添加一个回退方案来服务媒体文件
    # 注意：在真实的生产环境部署时，这一段代码必须被删除或注释掉！
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
