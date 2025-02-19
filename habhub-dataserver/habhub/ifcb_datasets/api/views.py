import environ
import hashlib
import json
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
)
from .mixins import DatasetFiltersMixin, BinFiltersMixin


# CACHE_TTL = env("CACHE_TTL", default=60 * 60)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


def create_cache_key(request, pk=0):
    print(request.query_params)
    qp_encoded = json.dumps(request.query_params, sort_keys=True).encode()
    qp_hash = hashlib.md5(qp_encoded)
    print(qp_hash.hexdigest())
    cache_key = f"{request.path}:{qp_hash.hexdigest()}:{pk}"
    print(cache_key)
    return cache_key


class DatasetBasicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetBasicSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ["dashboard_id_name"]


class AutoclassScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AutoclassScore.objects.all()
    serializer_class = AutoclassScoreSerializer
    pagination_class = StandardResultsSetPagination


class BinMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bin.objects.all()
    serializer_class = BinSerializer
    pagination_class = StandardResultsSetPagination


class BinViewSet(BinFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BinSerializer
    lookup_field = "pid"

    def get_queryset(self):
        queryset = Bin.objects.filter(cell_concentration_data__isnull=False)
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset

    @action(detail=True, methods=["get"])
    def get_species_images(self, request, pid):
        obj = self.get_object()
        species_name = request.query_params.get("species", None)

        # API request is sending display name
        target_list = TargetSpecies.objects.all()
        species = next(
            (item for item in target_list if item.display_name == species_name), False
        )

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
