from django.urls import path
from .views import (
    LabelcraftLoginView,
    logout_view,
    signup_step1,
    signup_org,
    org_join_requests_list,
    approve_org_join_request,
)

urlpatterns = [
    path('login/', LabelcraftLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_step1, name='signup'),
    path('signup/org/', signup_org, name='signup_org'),
    path('org/requests/', org_join_requests_list, name='org_join_requests'),
    path('org/requests/<int:request_id>/approve/', approve_org_join_request, name='approve_org_join_request'),
]
