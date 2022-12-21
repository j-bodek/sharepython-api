from django.urls import path
from codespace.views import CreateCodeSpaceView

app_name = "codespace"
urlpatterns = [
    path("codespace/", CreateCodeSpaceView.as_view(), name="create_codespace"),
]
