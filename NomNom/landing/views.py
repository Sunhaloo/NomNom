from django.http import HttpResponse


# our very first view
def index(request):
    return HttpResponse("Hello World From Index Page")
