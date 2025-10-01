# S.Sunhaloo

This is my space, don't fucking touch this!!!

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
