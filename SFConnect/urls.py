from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import LoginView
from . import views
urlpatterns=[
	path('login123/',views.login123,name='login123'),
	path('login/',views.login_view,name='login'),
	path('connect/',views.connect,name='connect'),
	#url(r'^index/$', views.index),
	#url(r'^getaccess/$', views.getaccess),
	url(r'^fetchLeads/$', views.fetchLeads),
	path('logout/',views.logout_view,name='logout'),]
    #url(r'^accounts/login/$')]
#handler404 = 'views.error_404'
#handler500 = 'views.error_500'