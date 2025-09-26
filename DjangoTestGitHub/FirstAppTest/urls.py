from django.urls import path
from . import views

urlpatterns = [
    # as I don't want the user to type a specific URL
    # for example instead of 'test_app/something_here'
    # I just want to get access quickly therefore 'test_app'
    path("index", views.index, name="index"),
    path("hello_world", views.hello_world, name="hello world"),
    # NOTE: if wanted to do 'test_app/something'
    # would have typed 'something/' and passed that as
    # our first arguement in the `path` function
]
