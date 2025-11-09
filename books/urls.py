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
from django.urls import path, include
from . import views

urlpatterns = [
    path('detail/<int:book_id>', views.detail, name='books_detail'),
    path('read/<int:book_id>', views.read, name='books_read'),
    path('search/', views.search, name='books_search'),
    path('searchview/', views.search_view, name='books_search_result'),
    path('tag/<int:tag_id>/', views.tag_books_view, name='tag_books'),
    path('add_to_bookshelf/<int:book_id>/', views.add_to_bookshelf, name='add_to_bookshelf'),
    path('bookself/', views.bookshelf, name='books_bookself'),
]
