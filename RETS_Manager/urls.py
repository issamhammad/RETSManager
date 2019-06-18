from django.contrib import admin
from django.conf.urls import include,url

urlpatterns = [
]

urlpatterns.append(url(r'^', include('web_app.urls')))
