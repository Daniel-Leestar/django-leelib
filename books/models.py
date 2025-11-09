from django.db import models

from login.models import User


# 书本标签模型
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# 书本模型
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/')  # 封面图片
    file = models.FileField(upload_to='books/')  # PDF文件
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(blank=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    # [新增] 覆盖 delete 方法以删除文件
    def delete(self, *args, **kwargs):
        # 1. 删除封面文件 (cover)
        # .delete() 方法会先检查文件是否存在，然后删除它
        if self.cover:
            self.cover.delete()
        # 2. 删除书本文件 (file)
        if self.file:
            self.file.delete()
        # 3. 调用父类的 delete 方法，执行数据库删除操作
        super().delete(*args, **kwargs)


#
# 收藏模型
class CollectRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    collect_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} 借了 {self.book.title}"
