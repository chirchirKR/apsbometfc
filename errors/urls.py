from django.urls import path
from . import views

app_name = "errors"

urlpatterns = [
    # Optional preview routes. Remove these in production if you do not want
    # public URLs that deliberately return error status codes.
    path("preview/400/", views.bad_request, name="preview_400"),
    path("preview/403/", views.permission_denied, name="preview_403"),
    path("preview/404/", views.page_not_found, name="preview_404"),
    path("preview/500/", views.server_error, name="preview_500"),
]
