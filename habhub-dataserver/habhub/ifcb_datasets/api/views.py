import environ
import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from habhub.core.models import TargetSpecies
from ..models import Dataset, Bin, AutoclassScore
from .serializers import (
    DatasetListSerializer,
    DatasetDetailSerializer,
    BinSerializer,
    BinSpatialGridSerializer,
    BinSpatialGridDetailSerializer,
    AutoclassScoreSerializer,
    DatasetBasicSerializer,
    CruiseTrackViewSetSerializer
)
from .mixins import DatasetFiltersMixin, BinFiltersMixin
from .cache_utils import create_cache_key


# CACHE_TTL = env("CACHE_TTL", default=60 * 60)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class DatasetBasicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetBasicSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ["dashboard_id_name"]


class AutoclassScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AutoclassScore.objects.select_related("bin", "species")
    serializer_class = AutoclassScoreSerializer
    pagination_class = StandardResultsSetPagination


class BinMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bin.objects.select_related("dataset")
    serializer_class = BinSerializer
    pagination_class = StandardResultsSetPagination


class BinViewSet(BinFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BinSerializer
    lookup_field = "pid"

    def get_queryset(self):
        queryset = Bin.objects.select_related("dataset").filter(
            cell_concentration_data__isnull=False
        )
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset

    @action(detail=True, methods=["get"])
    def get_species_images(self, request, pid):
        obj = self.get_object()
        species_name = request.query_params.get("species", None)

        # API request is sending display name
        species = TargetSpecies.objects.filter(display_name=species_name).first()

        bin_images_json = {}
        images = []

        if obj and species:
            data = obj.get_concentration_data_by_species(species.species_id)
            image_numbers = data["image_numbers"][:30]
            public_url = obj.dataset.dashboard_public_url
            if not public_url:
                public_url = obj.dataset.dashboard_base_url

            for img_name in image_numbers:
                img_path = (
                    f"{public_url}/{obj.dataset.dashboard_id_name}/{img_name}.png"
                )
                # need to check is this image exists locally. If not, go get it and cache locally
                # _get_image_ifcb_dashboard(bin_obj.dataset, img_name)
                # img_path = F"media/ifcb/images/{img_name}.png"
                images.append(img_path)

            bin_images_json = {
                "bin": {
                    "pid": obj.pid,
                    "dataset_id": obj.dataset.dashboard_id_name,
                    "dataset_link": public_url,
                },
                "species": species.display_name,
                "images": images,
            }

        return Response(status=status.HTTP_200_OK, data=bin_images_json)


class DatasetViewSet(DatasetFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DatasetListSerializer
    detail_serializer_class = DatasetDetailSerializer
    """
    @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    """

    def get_queryset(self):
        queryset = Dataset.objects.all().defer("bins")
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset

    # return different sets of fields if the request is list all or retrieve one,
    # so use two different serializers
    def get_serializer_class(self):
        if self.action == "retrieve":
            if hasattr(self, "detail_serializer_class"):
                return self.detail_serializer_class

        return super(DatasetViewSet, self).get_serializer_class()


class BinSpatialGridViewSet(BinFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        cache_key = create_cache_key(request)
        cached_data = cache.get(cache_key)
        print(datetime.datetime.now())
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        print("RUNNING QUERY")
        print("USER", request.user)
        queryset = Bin.objects.filter(
            cell_concentration_data__isnull=False, geom__isnull=False
        )
        queryset = self.handle_query_param_filters(queryset)
        serializer = BinSpatialGridSerializer(queryset, context={"request": request})
        # set cache
        cache.set(cache_key, serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        cache_key = create_cache_key(request, pk)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)
        # use the unique Geohash for the pk lookup
        queryset = Bin.objects.filter(
            cell_concentration_data__isnull=False, geom__isnull=False
        )
        queryset = self.handle_query_param_filters(queryset)

        serializer = BinSpatialGridDetailSerializer(
            queryset, context={"request": request, "geohash": pk}
        )
        # set cache
        cache.set(cache_key, serializer.data)
        return Response(serializer.data)

# Viewset to show full cruise track of vessel-based Datasets
class CruiseTrackViewSet(DatasetFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = CruiseTrackViewSetSerializer

    def get_queryset(self):
        queryset = Dataset.objects.filter(fixed_location=False).defer('bins')
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset
