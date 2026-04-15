# Flet - Mobile Application

## Installation Of Flet

> [!WARNING]
> Going to use the simple `pip` Python package manager as its the only thing that I know right now.
>
> One day I will take the time to learn about `uv` as its built using 'Rust'!

> Hopefully, you know how to create and enable the Python Virtual Environment

```bash
# install and/or upgrade to the latest version if possible
pip install -U 'flet[all]'
```

## Creation Of Flet Application

```bash
# initialise the flet project
flet create
```

### Running The "Thing"

- Run as desktop app / program:

```bash
flet run
```

- Run as web app:

```bash
flet run --web
```

- Run as mobile app:

> [!INFO]
>
> - Official Documentation: <https://flet.dev/docs/getting-started/testing-on-mobile>

Even if you are on Android or IOS; you are going to have to install the mobile application for Flet!

```bash
# Android-based phones
flet run --android

# IOS-based phones
flet run --ios
```
