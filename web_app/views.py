import os

from django.http import StreamingHttpResponse
from RETS_Manager.settings import BASE_DIR
from ddf_manager import manager as ddf_manager


def home_page(request):
    content = open(os.path.join(BASE_DIR, 'documenation.txt')).read()
    response = StreamingHttpResponse(content)
    response['Content-Type'] = 'text/plain; charset=utf8'
    return response

def test_ddf(request):
    ddf_manager.update_server(sample=True)
    content = open(os.path.join(BASE_DIR, 'ddf_client.log')).read()
    response = StreamingHttpResponse(content)
    response['Content-Type'] = 'text/plain; charset=utf8'
    return response

