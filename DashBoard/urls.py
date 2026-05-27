from django.urls import path
from . import views

urlpatterns = [
    path("", views.host_dashboard, name="host_dashboard"),
    path("responses/<int:form_id>/", views.view_responses, name="view_responses"),
    path("analytics/<int:form_id>/", views.form_analytics, name="form_analytics"),
]