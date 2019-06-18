from django.conf.urls import  url, handler404,handler500

import web_app.views
from django.conf import settings
# from web_app import views as core_views



#URL goes in sequence based on priority, order is important
urlpatterns = [
]

urlpatterns.append(url(r'^test/$', web_app.views.test_ddf))
urlpatterns.append(url(r'', web_app.views.home_page))