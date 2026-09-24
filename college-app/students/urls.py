from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^students/?$", views.student_list),
    re_path(r"^students/(?P<student_id>[^/]+)/?$", views.student_detail),
    re_path(r"^health/?$", views.health),
    re_path(r"^health/ready/?$", views.ready),
]
