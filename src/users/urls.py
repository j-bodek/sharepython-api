from django.urls import re_path
from users.views import RetrieveUpdateDestroyUserView

urlpatterns = [
    re_path(
        r"user/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/",
        RetrieveUpdateDestroyUserView.as_view(),
        name="retrieve_update_destroy_user",
    )
]
