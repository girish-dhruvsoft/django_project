"""SFConnection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from SFConnect import views
from django.conf.urls import handler404, handler500
#from SFConnect import views as my_views
urlpatterns = [
	path('accounts/login/', admin.site.urls),
    path('',include('SFConnect.urls')),
    path('api-auth/',include('rest_framework.urls')),
    path('api/token/',TokenObtainPairView.as_view()),
    path('api/token/refresh/',TokenRefreshView.as_view())]
handler404 = views.handler404
handler500 = views.handler500