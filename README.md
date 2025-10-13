> [!WARNING]
> DO NOT PUSH THE FUCKING PYTHON VIRTUAL ENVIRONMENT ITSELF!!!

# Main Branch

## Tracking The Commands I Ran ( Myself )

- Creating the Python Virtual Environment

```bash
# create the python virtual environment with the name 'Django'
python -m venv Django
```

- Source / Activate the Python Virtual Environment

```bash
# UNIX/LINUX Based Systems
source bin/activate

# On Windows Based Systems --> something along the lines of
./Scripts/activate
```

- Create **my** TMUX environment ( **you don't need to do this** )

```bash
# create my little TMUX world / environment
tmux new -s django
```

### Installing Django On Virtual Environment

- Install 'Django' package using `pip` command

```bash
# install the latest version of Django
pip install Django
```

- Check if 'Django' has been install successfully / correctly

```bash
# check the version of 'Django' installed
# running the command below should output something '5.2.6'
python -m django --version
```

- Freeze the current dependencies installed

```bash
pip freeze > requirements.txt
```

> [!NOTE]
> To install modules from the `requirements.txt` file, you need to run the following `pip` command:
>
> ```bash
> # install the required dependencies from `requirements.txt` file
> pip install -r requirements.txt
> ```

> I suggest you all to install using the `requirements.txt` file as you never know if there might be a version change of Django when we are working!!!

- Start the Django 'NomNom' **main** Project

```bash
# create the actual Django 'NomNom' project
# if creation is successfull... change the directory
django-admin startproject NomNom && cd NomNom
```

# Create The Main Templates Folder For The Whole Website

- Create a new `templates` directory inside the `NomNom` folder

```bash
# create main templates directory for the whole 'NomNom' website
mkdir templates
```

This is how my directory structure looks like:

```console
 .
├──  manage.py
├──  NomNom
│   ├──  __init__.py
│   ├──  asgi.py
│   ├──  settings.py
│   ├──  urls.py
│   └──  wsgi.py
└──  templates
```

# Change Some Of The Settings

I am now into the "_other_" 'NomNom' folder and opening the `NomNom/settings.py` file!

## Change Where Main Templates Are Located At

- Let Django know / Provide the path to our _main_ `templates` folder

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # change the default template location
        # no need to use something like string concatenation or `os.path.join`
        "DIRS": [BASE_DIR / "templates"],
        # We also want Django to find specific `<application_name>/templates` folder
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
```

## Change The Time Zone

Running my `timedatectl` command; I get the following output:

```console
               Local time: Wed 2025-10-01 16:55:03 +04
           Universal time: Wed 2025-10-01 12:55:03 UTC
                 RTC time: Wed 2025-10-01 12:55:03
                Time zone: Indian/Mauritius (+04, +0400)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

Therefore we going to change the `TIME_ZONE` variable from 'UTC' to 'Indian/Mauritius'

```python
TIME_ZONE = "Indian/Mauritius"
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
