from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello World From First App Index Method")


def hello_world(request):
    return HttpResponse("Hello World From First App 'hello_world' Method")
