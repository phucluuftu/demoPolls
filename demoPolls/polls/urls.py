from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    # url for view template
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:pk>/results/', views.result, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # url for api
    path('api/user/get/', views.user_get),
    path('api/user/vote/', views.user_vote_post),
    path('api/question/get/', views.question_get),
    path('api/question/search/', views.question_search),
    path('api/question/create/', views.question_create),
    path('api/result/get/<int:pk>', views.result_get)
]
