from django.urls import path
from . import views
app_name = "loop_auth"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
