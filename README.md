# S.Sunhaloo

This is my space, don't fucking touch this!!

> Its for me to test and fuck shit up!

---

# Rudimentary Setup For Work

- Creation of the `landing/views.py` file:

```python
from django.http import HttpResponse


# our very first view
def index(request):
    return HttpResponse("Hello World From Index Page")
```

- Creation of a "_test table_" inside the `landing/models.py` file

```python

from django.db import models


# WARNING: this is merely for show
class Test(models.Model):
    # create a test name field
    name = models.CharField(max_length=20)
```

- Register the application inside the `landing/admin.py` so that the admin page sees our table / model

```python
from django.contrib import admin

# WARNING: testing - import our test model
from .models import Test

# register the model here
admin.site.register(Test)
```

- Creation of the `landing/urls.py` file

```python
from django.urls import path
from . import views

# define the application name to avoid Django making confusion down the line
app_name = "landing"

# create inner application routings
urlpatterns = [
    # our default page
    path("", views.index, name="index")
]
```

## Going Back To NomNom Project Folder

- Add the following line to the `INSTALLED_APPS` Python list inside `settings.py` file

```python
INSTALLED_APPS = [
    # add our specific landing page application
    "landing.apps.LandingConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

- Link our "_view_" to the whole project

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # WARNING: the order of "operations" matter
    path("landing/", include("landing.urls")),
    path("admin/", admin.site.urls),
]
```

## Running Django Specific Commands

- Make the migrations:

```bash
# create the plan for Django for the models
python manage.py makemigrations
```

- Actually write to the `db.sqlite3` file using the `migrate` command:

```bash
# create the plan for Django for the models
python manage.py migrate
```

## Creation Of Superuser

- Ran the following command to create the `test` superuser with `1234` as passwords
- Ran the following command to create the `test` superuser

```bash
python manage.py createsuperuser --username "test" --email "test@email.com"

```

| Username | Email            | Password |
| -------- | ---------------- | -------- |
| test     | <test@email.com> | 1234     |

### Run The Django Development Server

- To run the Django development server:

```bash
# run the Django development server
python manage.py runserver
```

---

# Templates and Render

## Setup Files And Folders

- Head over to the _main_ project file and create these two folders

```bash
# create the outer templates and static folder
mkdir templates static
```

> [!NOTE]
>
> - The `templates` directory is going to hold all of our **global** `.html` file that can be called from _any_ application using the `{% extends "page.html" %}`
> - The `static` directory is going to hold all of our **global** _styling_ for our `templates/*.html` files!
>
> But currently Django does not know that we have these two directories outside and still things that we are going to have everything inside our applications.
>
> > Hence, we are going to have to modify our `NomNom/settings.py` file!

- Configure Our `NomNom/settings.py` file:

```python
# < other codes here >

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # change the default template location
        # no need to use something like string concatenation or `os.path.join`
        "DIRS": [BASE_DIR / "templates"],
        # we also want Django to find specific `<application_name>/templates` folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# < other codes here >

STATIC_URL = "static/"

# global directory of where the static files are found ( in project )
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

## Global Templates And Static Files

### Creation Of Templates / HTML Files

Head over into our `templates` _global_ directory and create _some_ HTML files!

- Create our "_test_" `base.html` file:

```html
<!doctype html>
<html lang="en">
  <head>
    <!-- tell Django to load the files inside `static` folder -->
    {% load static %}

    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <!-- add a global title -->
    <title>{% block title %}NomNom{% endblock %}</title>
    <!-- link the main style sheet found in `static` folder -->
    <link href="{% static 'style.css' %}" rel="stylesheet" />
  </head>
  <body>
    <!-- include the navigation bar at the top of `base.html` file -->
    {% include 'navbar.html' %}
    <!-- this should appear from the global `base.html` file -->
    <h1>Hello World From Global Templates!!!</h1>

    <!-- make sure that each application can override `.html` file -->
    {% block content %}
    <!-- applications overridden contents goes here -->
    {% endblock %}

    <!-- include the footer at the bottom of `base.html` file -->
    {% include 'footer.html' %}
  </body>
</html>
```

- Create our "_test_" `navbar.html` file:

```html
<!-- tell Django to load the files inside `static` folder -->
{% load static %}

<!-- start of the navigation bar area -->
<nav>
  <!-- test the navigation bar -->
  <h4>This is our navigation bar</h4>
</nav>
```

- Create our "_test_" `footer.html` file:

```html
<!-- tell Django to load the files inside `static` folder -->
{% load static %}

<!-- start of the footer area -->
<footer>
  <!-- test the footer -->
  <h4>This is our footer bar</h4>
</footer>
```

### Creation Of Static / CSS Files

Head over into our `static` _global_ directory and create _some_ CSS files!

- Create our "_test_" `style.css` file:

```css
html {
  background-color: black;
  color: white;
}
```

## Landing Page Templates And Static Files

We are now going to setup the "_inner_" `templates` and `static` directories inside our `landing` Django application / folder.

- Head over into our 'landing' Django application and create the directories:

```bash
# create the 'templates' and 'static' directories
mkdir -p templates/landing
mkdir -p static/landing
```

### Creation Of `landing.html` File

- Head inside the `templates/landing` directory and create the `landing.html` file:

```html
<!-- call our `base.html` file from global templates -->
{% extends "base.html" %}

<!-- tell Django to load the files inside `static` folder -->
{% load static %}

<!-- modify the tab name for our landing page -->
{% block title %} Landing Page {% endblock %}

<!-- content that will be found inside the `landing.html` page specifically -->
{% block content %}
<h2>Hello World From Landing Page</h2>
{% endblock %}
```

> [!WARNING] Modify Our `templates/base.html`
> In order to be able to use the "_inner_" `static/landing/style.css` file.
> We first need to tell Django that we do have this file there.
>
> Hence modify the `templates/base.html` file and add this following line in the `head` tag:
>
> ```html
> <link href="{% static 'landing/style.css' %}" rel="stylesheet" />
> ```

### Creation Of `style.css` File

- Head inside the `static/landing` directory and create the `style.css` file:

```css
h2 {
  color: cyan;
  text-align: center;
}
```

> [!SUCCESS]
> This should be enough now! Run the development server to test.
>
> ```bash
> python manage.py runserver
> ```

---

# Create And Setup New Login Application

- Run the `startapp` sub-command to create the `login` application

```bash
# with the Python virtual environment started
# create the `login` application using the `manage.py` file
python manage.py startapp login
```

- Create the `templates/login` and `static/login` directories

```bash
mkdir -p templates/login
mkdir -p static/login
```

- Create the `login.html` file inside the `templates` directory:

```html
<!-- call the `base.html` template file -->
{% extends 'base.html' %}

<!-- load the `login/static/login/style.css` file -->
{% load static %}

<!-- change the title of the webpage -->
{% block title %} NomNom Login {% endblock %}

<!-- the actual content for the login page -->
{% block content %}
<h4>Hey You! Are You Good?</h4>
{% endblock %}
```

- Create the `style.css` file inside the `static` directory:

```css
h4 {
  color: purple;
}
```

- Setup the view inside the `views.py` file:

```python
from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    # return HttpResponse("Hello World From Login")
    return render(request, "login/login.html")
```

- Create a fake 'model' / table inside the `models.py` file:

```python
from django.db import models


# Create your models here.
class Test(models.Model):
    test_name = models.CharField(max_length=200)
```

- Create the inner links by creating a new `urls.py` file:

```python
from django.urls import path
from . import views

# define the app name here so that Django does not get confused with URLs
app_name = "login"

urlpatterns = [
    # our login path
    path("", views.index, name="login")
]
```

- Register the model to the admin "website" inside `admin.py`:

```python
from django.contrib import admin

# import our "class" definition / tables from model
from .models import Test

# Register your models here.
admin.site.register(Test)
```

## Inside The Main Project Folder

- Link the `login` app to the whole project in the `urls.py` file:

```python
urlpatterns = [
    # WARNING: the order of "operations" matter
    # add the main landing page for the website
    path("", include("landing.urls")),
    # add the login page that will allow the user to handle login of users
    path("login/", include("login.urls")),
    path("admin/", admin.site.urls),
]
```

- Add the new application to the `INSTALLED_APPS` Python list inside the `settings.py` file:

```python
INSTALLED_APPS = [
    # add our specific landing page application
    "landing.apps.LandingConfig",
    # add our specific login page application
    "login.apps.LoginConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

---

# Change The Load Order Of Style Sheets

- Modify the `base.html` so that this part below looks like this:

```html
<link href="{% static 'landing/style.css' %}" rel="stylesheet" />
<link href="{% static 'login/style.css' %}" rel="stylesheet" />
<link href="{% static 'style.css' %}" rel="stylesheet" />
```

> [!INFO]
> If we want the outer `NomNom/static/style.css` file to take _control_; the order we `link` the stylesheet is **important**!

---

# Creation Of All Of The Other Applications

> [!NOTE]
> I have now created three more applications:
>
> - About Us Application
> - Contact Application
> - Cart Application
>
> I used the **same** process to be able to _render_ and display the "_webpages_"!

> [!TIP]
>
> > A little thing that I found!
>
> Let's say that in our `contact/views.py` file inside the `render` function for passing the template **instead** of writing something like `"contact/contact.html"`
>
> Instead of that, we wrote something like `"landing/landing.html"`... **No errors** would be found!
>
> It will simply go ahead and use that _inner_ specific application template ( _if found_ ) and will **not** cause any trouble.

---

# Developing On Login App

## Creation Of New Superuser

| Username    | Email                  | Password |
| ----------- | ---------------------- | -------- |
| first_admin | <firstadmin@email.com> | 1234     |

#### Trouble Creating Superusers

As we have now moved everything from the `landing` app and into the `login` app.

We just _deleted_ everything in terms of the database and re-ran the following commands:

- Make the migrations ( _overall_ ) and also for the `login` app:

```bash
# make the overall migrations
python manage.py makemigrations

# make the migrations for the login app
python manage.py makemigrations login
```

- Actually ask Django to write to the database `db.sqlite3`:

```bash
# create the tables
python manage.py migrate
```

> [!TIP] `find` Command Used To Delete Python Cache Directories
>
> - Here is the command that I used to find and delete all the `__pycache__` directories:
>
> ```bash
> # this should be ran from the root of the `NomNom` directory
>   find . -type d -name "__pycache__" -exec rm -rf {} +
> ```

#### Fixing Inability To Create Superusers

Here are the steps that I tool to be able to make it work again.

> Remember we are trying to move the "_data_" inside `landing/models.py` to `login/models.py`!

1. Delete all the other unnecessary tables created in other applications like `about_us`, `cart` and `contact`
   a. This means removing the _contents_ inside the applications' `models.py` and `admin.py` files
2. Delete all the `migrations` folder found in **each** application ( _folder_ )
3. Delete all the `__pycache__` folders --> ( _just to make sure and be safe that's its going to work_ )
4. Move the contents found inside the `landing/models.py` file to `login/models.py`
5. Also remove the contents from `landing/admin.py` and move to `login/admin.py`
6. Finally change `AUTH_USER_MODEL = "landing.User"` to `AUTH_USER_MODEL = "login.User"`
7. Hence, these following commands in order:
   a. `python manage.py makemigrations`
   b. `python manage.py makemigrations login`
   c. `python manage.py migrate`

Therefore, simply create our new superuser with the following command:

```bash
# create our new "first" superuser
python manage.py createsuperuser --username first_admin --email firstadmin@email.com
```

> Hence, simply run Django's development server and you should now be able to log into the 'admin' website!

## Using Python Interactive Shell To Create Users

Below you are going to learn how the code _look_ like to create a **customer** <strong><span style="color: orange";>Sign Up</span></strong>!!!

- Open / Start the Python Interactive Shell:

```bash
# start the interactive shell with the following command
python manage.py shell
```

- Import the `User` ( _user-defined / updated_ ) model:

```python
# import the 'User' "table"
from login.models. import User
```

- Create a new customer:

```python
# I know its misleading with the variable name
new_user = User.objects.create_user(
    username="john_doe",
    email="john@example.com",
    password="strongpassword123",
    first_name="John",
    last_name="Doe",
    gender="M",
    region="Port Louis",
    street="Royal Road"
)
```

- Check if the `CUSTOMER` "_user_" has been created:

```python
# list all the 'CUSTOMER' users found in the `User` tables
User.objects.filter(role="CUSTOMER")
```

- Therefore, in this case, we should get the following output:

```console
<QuerySet [<User: john_doe>]>
```

---

## Form To Allow Users To Sign Up

This is how we implemented the `form.py` that is going to be responsible for allowing our users to **sign up**.

- Create the `forms.py` file in our `NomNom/login` folder / application:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "auth-input", "placeholder": "Email"}),
    )
    gender = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female")],
        widget=forms.Select(attrs={"class": "auth-input"}),
    )
    first_name = forms.CharField(
        max_length=80,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "placeholder": "Last Name"}
        ),
    )
    region = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Region"}),
    )
    street = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Street"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "gender",
            "region",
            "street",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Confirm Password"}
        )
```

- Write the _back-end logic_ for displaying the form:

```python
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from .forms import SignupForm

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data.get("password1")
            )  # Use password1 from form
            user.save()
            return redirect("login:login")
    else:
        form = SignupForm()

    return render(request, "login/signup.html", {"form": form})
```

The above code is going to check if the data has been sent to the "_database_" using the 'POST' method ( _user is sending data to save_ ). If so then send all the data that the user entered on the 'Sign Up' form. Then its going to redirect the user to the login page so that he / she can login with the new credentials.

- Update the front-end ( _i.e `login/templates/signup.html`_ ) to be able to see the changes:

```html
{% if form.non_field_errors %}
<div class="error-message" style="color:red; text-align:center;">
  {% for error in form.non_field_errors %} {{ error }} {% endfor %}
</div>
{% endif %}

<form method="POST" action="{% url 'login:signup' %}" class="auth-form">
  {% csrf_token %}

  <!-- Username -->
  {{ form.username }} {% if form.username.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.username.errors }}
  </div>
  {% endif %}

  <!-- Email -->
  {{ form.email }} {% if form.email.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.email.errors }}
  </div>
  {% endif %}

  <!-- Password1 -->
  {{ form.password1 }} {% if form.password1.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.password1.errors }}
  </div>
  {% endif %}

  <!-- Password2 -->
  {{ form.password2 }} {% if form.password2.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.password2.errors }}
  </div>
  {% endif %}

  <!-- First Name -->
  {{ form.first_name }} {% if form.first_name.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.first_name.errors }}
  </div>
  {% endif %}

  <!-- Last Name -->
  {{ form.last_name }} {% if form.last_name.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.last_name.errors }}
  </div>
  {% endif %}

  <!-- Gender -->
  {{ form.gender }} {% if form.gender.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.gender.errors }}
  </div>
  {% endif %}

  <!-- Region -->
  {{ form.region }} {% if form.region.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.region.errors }}
  </div>
  {% endif %}

  <!-- Street -->
  {{ form.street }} {% if form.street.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.street.errors }}
  </div>
  {% endif %}

  <button type="submit" class="auth-btn">Signup</button>
</form>
```

## Form To Allow Users To Log In

- Update the `login/forms.py` so that users are able to use their credentials to login:

```python
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "placeholder": "Username"}
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "auth-input", "placeholder": "Password"}
        ),
    )
```

- Update the `views.py` file to be able to render out the form:

```python
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from .forms import SignupForm, LoginForm

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("landing:landing")
    else:
        form = LoginForm()
    return render(request, "login/login.html", {"form": form})
```

> [!NOTE]
> The `index` function is not change to the above `login_view` function!

- Update the `/login/templates/login/login.html` template to be able to actually see the form:

```html
{% if form.non_field_errors %}
<div class="error-message" style="color:red; text-align:center;">
  {% for error in form.non_field_errors %} {{ error }} {% endfor %}
</div>
{% endif %}

<form method="POST" action="{% url 'login:login' %}" class="auth-form">
  {% csrf_token %}

  <!-- Username -->
  {{ form.username }} {% if form.username.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.username.errors }}
  </div>
  {% endif %}

  <!-- Password -->
  {{ form.password }} {% if form.password.errors %}
  <div class="error-message" style="color:red; font-size: 0.8em;">
    {{ form.password.errors }}
  </div>
  {% endif %}

  <button type="submit" class="auth-btn">Login</button>
</form>
```

- Additionally, we have to update our `templates/navbar.html` to show the log out button if user has been logged in:

```html
{% if user.is_authenticated %}
<li><a href="{% url 'login:login' %}">Log Out</a></li>
{% else %}
<li><a href="{% url 'login:login' %}">Log in</a></li>
{% endif %}
```

## Log Out User

> Actually the above 'HTML' snippet is not good!

- Update our `login/views.py` file like so:

```python
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from .forms import SignupForm, LoginForm


def logout_view(request):
    logout(request)
    return redirect("landing:landing")
```

- Update the `login/urls.py` file to add the new inner routing:

```python
from django.urls import path
from . import views

# define the app name here so that Django does not get confused with URLs
app_name = "login"

urlpatterns = [
    # our login path
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
]
```

- Finally, update the actual `template/navbar.html` file so that's it correctly displays the links:

```html
{% if user.is_authenticated %}
<li><a href="{% url 'login:logout' %}">Log Out</a></li>
{% else %}
<li><a href="{% url 'login:login' %}">Log in</a></li>
{% endif %}
```
