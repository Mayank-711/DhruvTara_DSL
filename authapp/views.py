from django.shortcuts import render

# Create your views here.
def landingpage(request):
    return render(request,'authapp/landingpage.html')


def login(request):
    return render(request,'authapp/login.html')