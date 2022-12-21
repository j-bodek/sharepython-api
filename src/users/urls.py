from django.urls import path
from users.views import RetrieveUpdateDestroyUserView

app_name = "users"
urlpatterns = [
    path(
        "user/",
        RetrieveUpdateDestroyUserView.as_view(),
        name="retrieve_update_destroy_user",
    )
]
