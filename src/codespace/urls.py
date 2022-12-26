from django.urls import path, re_path
from codespace.views import (
    CreateCodeSpaceView,
    RetrieveCodeSpaceView,
    TokenCodeSpaceAccessView,
    RetrieveCodeSpaceAccessTokenView,
    TokenCodeSpaceAccessVerifyView,
)

app_name = "codespace"
urlpatterns = [
    path("codespace/", CreateCodeSpaceView.as_view(), name="create_codespace"),
    re_path(
        r"codespace/(?P<uuid>(tmp-)?[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/",  # noqa
        RetrieveCodeSpaceView.as_view(),
        name="retrieve_codespace",
    ),
    # Big thx https://stackoverflow.com/a/5885097/14579046
    re_path(
        r"codespace/(?P<token>(?:[a-zA-Z0-9_-]{4})*(?:[a-zA-Z0-9_-]{2}==|[a-zA-Z0-9_-]{3}=|[a-zA-Z0-9_-]{4}))/",  # noqa
        RetrieveCodeSpaceAccessTokenView.as_view(),
        name="retrieve_codespace_access_token",
    ),
    path(
        "codespace/access/token/",
        TokenCodeSpaceAccessView.as_view(),
        name="token_codespace_access",
    ),
    path(
        "codespace/access/token/verify/",
        TokenCodeSpaceAccessVerifyView.as_view(),
        name="token_codespace_verify",
    ),
]
