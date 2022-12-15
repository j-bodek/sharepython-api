from django.urls import path
from users.views import RetrieveUpdateDestroyUserView

urlpatterns = [
    path(
        "user/",
        RetrieveUpdateDestroyUserView.as_view(),
        name="retrieve_update_destroy_user",
    )
]
