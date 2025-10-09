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
