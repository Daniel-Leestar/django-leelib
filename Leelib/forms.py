from django import forms
from books.models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # 你想在表单中显示的字段
        fields = [
            'title',
            'author',
            'cover',  # 图片
            'file',  # 文件
            'tags',
            'description',
            # 'uploader' 字段我们会在view里自动设置，不让用户选
        ]

        # (可选) 给字段添加一些HTML class，方便美化
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control-file'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
