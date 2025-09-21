"""
URL configuration for DhruvTara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import authapp.views as aviews
import students.views as sviews


urlpatterns = [
    path('admin/', admin.site.urls),
]


auth_views = [
    path('',aviews.landingpage,name='landingpage'),
    path('login/',aviews.login_view,name='login'),
    path('signup/',aviews.signup_view,name='signup'),
    path('logout/',aviews.logout_view,name='logout')
]


stud_urls = [
    path('dashboard/',sviews.dashboard,name='dashboard'),
    path('assessment/',sviews.assessment,name='assessment'),
    path('careerpath/',sviews.careerpath,name='careerpath')
]



urlpatterns += auth_views + stud_urls