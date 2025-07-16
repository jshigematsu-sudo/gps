from django.urls import path

from . import views

app_name = 'current_meet_locations'
urlpatterns = [
    path('', views.CreateMeetingMap.as_view(),name='create_meeting_map'),
    path('get_site_members/', views.GetSiteMembers.as_view(), name='get_site_members'),
    path('save_site_data/', views.SaveSiteData.as_view(), name='save_site_data'),
    path('save_member_data/', views.SaveMemberData.as_view(), name='save_member_data'),
    path('get_site_data/', views.GetSiteData.as_view(), name='get_member_data'),
    path('get_members_location/', views.GetMemberData.as_view(), name='get_members_location'),
    path('manage_site_member/', views.ManageSiteMember.as_view(), name='manage_site_member'),
    path('get_date_info/', views.GetDateInfo.as_view(), name='get_date_info'),
]
