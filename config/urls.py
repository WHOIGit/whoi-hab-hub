from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.gis import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from habhub.stations import views as stations_views
from habhub.closures import views as closures_views
from habhub.esp_instrument import views as esp_instrument_views

admin.site.site_header = 'WHOI HABHub Administration'                    # default: "Django Administration"
admin.site.index_title = 'Site administration'                 # default: "Site administration"
admin.site.site_title = 'WHOI HABHub Administration' # default: "Django site admin"

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
    path('', include('habhub.dashboard.urls', namespace='dashboard')),
    path('ajax/load-esp-deployment-data/', esp_instrument_views.load_esp_deployment_data, name='ajax_load_esp_deployment_data'),
    path('closures/', include('habhub.closures.urls', namespace='closures')),
    path('stations/', include('habhub.stations.urls', namespace='stations')),
    path('ifcb-datasets/', include('habhub.ifcb_datasets.urls', namespace='ifcb_datasets')),
    path('monitoring_systems/', include('habhub.monitoring_systems.urls', namespace='monitoring_systems')),
    #path('ifcb-cruises/', include('habhub.ifcb_cruises.urls', namespace='ifcb_cruises')),
    # API urls
    path('api/v1/', include('habhub.stations.api.urls')),
    path('api/v1/', include('habhub.ifcb_datasets.api.urls')),
    path('api/v1/closure-notices/', closures_views.ClosureNoticeAjaxGetAllView.as_view(), name='api_closure_notices_all'),
    # Summernote WYSIWYG
    path('summernote/', include('django_summernote.urls')),

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
