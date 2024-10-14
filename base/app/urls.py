from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('clients/', views.client_get_post, name='client_get_post'),
    path('clients/<int:id>/', views.client_get_put_delete, name='client_get_put_delete'),
    path('clients/<int:id>/projects/', views.create_project, name='create_project'),
    path('projects/', views.projects, name='project')
]