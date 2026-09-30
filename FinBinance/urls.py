from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from information.views import expansion_kpis


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("configurepage.urls")),
    path("user/accounts/", include("accounts.urls")),
    path("direct/accountings/", include("accountings.urls")),
    path("direct/information/", include("information.urls")),
    path("api/expansion-kpis/", expansion_kpis, name="expansion_kpis"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )