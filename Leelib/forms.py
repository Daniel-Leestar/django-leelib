from django import forms
from books.models import Book
from login.models import User


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


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser'
        )

        # 使用 widgets 来覆盖 name 属性，使其与自定义 HTML 表单匹配
        widgets = {
            # 注意：这里我们强制将 first_name 字段的 name 设为 'fist_name' (与您的HTML一致)
            'first_name': forms.TextInput(attrs={'name': 'fist_name', 'id': 'user_firstname', 'class': 'info-value'}),

            # last_name 字段名是 'last_name'
            'last_name': forms.TextInput(attrs={'name': 'last_name', 'id': 'user_lastname', 'class': 'info-value'}),

            # email 字段名是 'email'
            'email': forms.TextInput(attrs={'name': 'email', 'id': 'user_email', 'class': 'info-value'}),

            # Checkbox 字段
            'is_staff': forms.CheckboxInput(
                attrs={'name': 'staff', 'id': 'user_staff', 'style': 'line-height: 39px;cursor: pointer;'}),
            'is_superuser': forms.CheckboxInput(
                attrs={'name': 'superuser', 'id': 'user_superuser', 'style': 'line-height: 39px;cursor: pointer;'}),
        }
