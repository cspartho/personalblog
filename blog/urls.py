from django.urls import path
from .views import post_list,post_detail
from .feeds import LatestPostFeed

app_name='blog'

urlpatterns = [
    path('',post_list,name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',post_detail,name='post_detail'),
    path('tag/<slug:tag_slug>/',    post_list,name='post_list_by_tag'),
    path('feed/',LatestPostFeed(),name='post_feed'),
]
