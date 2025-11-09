from django.contrib import admin
from .models import Tag, Book, CollectRecord


# Register your models here.
# 书本标签模型管理界面
class SiteBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploader', 'upload_time')


admin.site.register(Book, SiteBookAdmin)

# 书本管理界面
class SiteBookTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Tag, SiteBookTagAdmin)

# 收藏管理界面
class SiteCollectRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'collect_time')


admin.site.register(CollectRecord, SiteCollectRecordAdmin)
