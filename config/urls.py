from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from habhub.stations import views as stations_views
from habhub.esp_instrument import views as esp_instrument_views

urlpatterns = [
    #path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path(
        "users/",
        include("habhub.users.urls", namespace="users"),
    ),
    path("accounts/", include("allauth.urls")),

    # Custom HAB urls
    path('', stations_views.StationListView.as_view(), name='home'),
    path('ajax/load-station-data/', stations_views.load_station_data, name='ajax_load_station_data'),
    path('ajax/load-esp-deployment-data/', esp_instrument_views.load_esp_deployment_data, name='ajax_load_esp_deployment_data'),
    path('ifcb-cruises/', include('habhub.ifcb_cruises.urls', namespace='ifcb_cruises')),

] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
