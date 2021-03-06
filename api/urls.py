from django.conf.urls import url

from home import search_api
from message.views import ConversationAPI
from message.views import ReplyAPI
from submission.views import submission_code_api, submission_count_api
from utils.markdown3 import markdown_convert_api

app_name = "api"


urlpatterns = [
    url(r'^submission/$', submission_code_api),
    url(r'^submission/user/(?P<name>.*)/$', submission_count_api),
    url(r'^markdown/$', markdown_convert_api),
    url(r'^search/$', search_api.SearchAPI.as_view(), name='search'),
    url(r'^search/user/$', search_api.SearchUserAPI.as_view(), name='user_search'),
    url(r'^search/problem/$', search_api.SearchProblemAPI.as_view(), name='problem_search'),
    url(r'^message/reply/(?P<pk>\d+)/$', ReplyAPI.as_view()),
    url(r'^message/c/(?P<pk>\d+)/$', ConversationAPI.as_view()),
]
