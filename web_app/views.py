import os

from django.http import StreamingHttpResponse
from RETS_Manager.settings import BASE_DIR
from ddf_manager import manager as ddf_manager

#Django views. To understand more about Django views, please check the documenation under:
#https://docs.djangoproject.com/en/1.9/topics/http/views/

#Home Page view. Loads the documenation
def home_page(request):
    content = open(os.path.join(BASE_DIR, 'documenation.txt')).read()
    response = StreamingHttpResponse(content)
    response['Content-Type'] = 'text/plain; charset=utf8'
    return response

#test_ddf view. Performs a sample update then displays the log file.
def test_ddf(request):
    ddf_manager.update_server(sample=True)
    content = open(os.path.join(BASE_DIR, 'ddf_client.log')).read()
    response = StreamingHttpResponse(content)
    response['Content-Type'] = 'text/plain; charset=utf8'
    return response

