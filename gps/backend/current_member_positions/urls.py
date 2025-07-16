# urls.py
from django.urls import path

from . import views

app_name = 'current_member_positions'
urlpatterns = [
    path('join_new_group/', views.JoinNewGroup.as_view(), name='join_new_group'),

    path('get_members_position/', views.GetMembersPosition.as_view(), name='get_members_position'),
]
