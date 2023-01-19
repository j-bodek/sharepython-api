from django.urls import path, re_path
from codespace import views

app_name = "codespace"
urlpatterns = [
    path("codespace/", views.CreateCodeSpaceView.as_view(), name="create_codespace"),
    re_path(
        r"codespace/save_changes/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/",  # noqa
        views.CodeSpaceSaveChangesView.as_view(),
        name="save_changes_codespace",
    ),
    re_path(
        r"codespace/(?P<tmp_uuid>tmp-[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/",  # noqa
        views.RetrieveDestroyTmpCodeSpaceView.as_view(),
        name="retrieve_destroy_tmp_codespace",
    ),
    re_path(
        r"codespace/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/",  # noqa
        views.RetrieveUpdateDestroyCodeSpaceView.as_view(),
        name="retrieve_update_destroy_codespace",
    ),
    # Big thx https://stackoverflow.com/a/5885097/14579046
    re_path(
        r"codespace/(?P<token>(?:[a-zA-Z0-9_-]{4})*(?:[a-zA-Z0-9_-]{2}==|[a-zA-Z0-9_-]{3}=|[a-zA-Z0-9_-]{4}))/",  # noqa
        views.RetrieveCodeSpaceAccessTokenView.as_view(),
        name="retrieve_codespace_access_token",
    ),
    path(
        "codespaces/",
        views.CodeSpaceListView.as_view(),
        name="list_codespaces",
    ),
    path(
        "codespace/access/token/",
        views.TokenCodeSpaceAccessCreateView.as_view(),
        name="token_codespace_access",
    ),
]
