from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    # Host side
    
    path("create-form/", views.create_form, name="create_form"),
    path("add-question/<int:form_id>/", views.add_question, name="add_question"),
    path("edit-question/<int:question_id>/", views.edit_question, name="edit_question"),
    path("delete-question/<int:question_id>/", views.delete_question, name="delete_question"),

    # Public feedback form
    path("form/<slug:slug>/", views.public_form, name="public_form"),
    path("thank-you/", views.thank_you, name="thank_you"),
]