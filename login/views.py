from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import check_password


# Create your views here.
def login_action(request):
    # if request.method == 'POST':
    #     email = request.POST.get('email')
    #     password = request.POST.get('password')
    #
    #     # 用 email 查找用户
    #     try:
    #         user = User.objects.get(email=email)
    #     except User.DoesNotExist:
    #         messages.error(request, "邮箱未注册")
    #         return render(request, 'login/login.html', {'err': "邮箱未注册"})
    #
    #     # 检查密码是否匹配
    #     if check_password(password, user.password):
    #         if user.is_active:
    #             # 登录成功后保存 session
    #             request.session['user_id'] = user.id
    #             request.session['user_fname'] = user.first_name
    #             request.session['user_lname'] = user.last_name
    #             messages.success(request, "登录成功！")
    #
    #             return redirect('/',{'user': user.id})  # 登录成功跳转主页
    #         else:
    #             messages.error(request, "账户未激活")
    #             return render(request, 'login/login.html', {'err': "账户未激活"})
    #     else:
    #         messages.error(request, "密码错误")
    #         return render(request, 'login/login.html', {'err': "密码错误"})

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            preUser = User.objects.get(email=email)
            if not preUser.is_active:
                return render(request, 'login/login.html', {'err': 'No active'})
        except User.DoesNotExist:
            preUser = None
            return render(request, 'login/login.html', {'err': 'No User with that email exists'})

        user = authenticate(request, email=email, password=password)
        if user:
            print("登录成功")
            login(request, user)  # 保存 session
            request.session['test'] = 1
            return redirect('/')
        else:
            print("Invalid email address or password")
            print(user)
            return render(request, 'login/login.html', {'err': 'Invalid email address or password'})

    return render(request, 'login/login.html')


def logout_action(request):
    logout(request)

    return redirect('/')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        print(request.POST)  # 调试：确认是否收到 POST 请求
        print("POST request received")  # 调试：确认是否收到 POST 请求
        if form.is_valid():
            print("Form is valid")  # 调试：确认表单是否有效
            form.save()
            messages.success(request, 'New account has been created!')
            return redirect('/login/')

        else:
            print("Form is invalid")  # 调试：确认表单是否无效
            errors = form.errors
            print(errors)  # 打印出错误信息
            form = CustomUserCreationForm()
            return render(request, 'login/register.html', {'err': errors})

    else:
        form = CustomUserCreationForm()

    return render(request, 'login/register.html', {'err': ""})


def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        # 1️⃣ 检查旧密码是否正确
        if not user.check_password(old_password):
            messages.error(request, '旧密码错误！')
            return render(request, 'login/modifypsw.html', {'err': 'Invalid old password!'})

        # 2️⃣ 检查两次新密码是否一致
        if new_password1 != new_password2:
            messages.error(request, '两次输入的新密码不一致！')
            return render(request, 'login/modifypsw.html', {'err': 'The new password entered twice does not match！'})

        # 3️⃣ 设置新密码并保存
        user.set_password(new_password1)
        user.save()

        # 4️⃣ 保持登录状态（否则会被登出）
        update_session_auth_hash(request, user)

        messages.success(request, '密码修改成功！')
        return redirect('/portfolio')  # 可改为你想跳转的页面

    return render(request, 'login/modifypsw.html')
