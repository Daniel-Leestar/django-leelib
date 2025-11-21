## How To Use 使用方法

### Deployment 部署

**Windows**  
Install **Python 3.12**.  
Download the source code from the project homepage, extract it, and double-click **`start_server_english.bat`** to launch the server.

 安装python3.12，在项目首页下载源代码解压后双击打开 **`start_server_english.bat`**

**macOS & Linux**  
Make sure **Python 3.12** (or a compatible version) is installed.  
Open a terminal in the project directory and install the required dependencies:

确保已安装 Python 3.12（或兼容版本）。
在项目目录中打开终端，安装所需依赖项：

```bash
pip install -r requirements.txt
```

Then start the server:

开启服务

```bash
python manage.py runserver
```

### Rules of user management 用户规则

Activated users: Can use the bookshelf and online preview features

Staff: Can upload books

Superuser: Has all permissions

Note: When creating a superuser, make sure to also check the Staff option.

仅激活账户: 使用书架、在线预览功能 

员工: 上传书本 

超级用户: 所有权限 

注意使用超级用户时必须选上员工

## Default admin username and password 默认管理员账号密码

Email(邮箱) root@leelib.com

Password(密码) 12345678

## Home Page 首页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/home.jpg)

## Detail Page 详情页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/detail.jpg)


## Read Page 阅读页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/read.jpg)

## Management Page 管理页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/manage.png)

## Login Page 登录页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/login.jpg)

## Sign-up Page 注册页

![image](https://github.com/Daniel-Leestar/django-leelib/blob/master/Preview%20Images/signup.jpg)

## Bug 漏洞

No major bugs have been found.
In the admin interface, duplicate email addresses or tag names may be accepted without showing any error notifications.

## Possible future updates 未来可能更新

Avatar upload，Website control panel (including changing the logo, site name, and more)

头像上传、网页总控制台（包括更改logo、网站名等）
