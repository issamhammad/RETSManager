from django.conf.urls import  url, handler404,handler500

import web_app.views

#For details check Django URL documenation design under:
#https://docs.djangoproject.com/en/1.9/topics/http/urls/

#URL goes in sequence based on priority, order is important
urlpatterns = [
]

urlpatterns.append(url(r'^test/$', web_app.views.test_ddf))
urlpatterns.append(url(r'', web_app.views.home_page))