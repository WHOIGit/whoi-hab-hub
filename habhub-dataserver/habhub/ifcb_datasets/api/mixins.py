import datetime

from django.db.models import Prefetch, F, Q
from django.utils import timezone
from django.utils.timezone import make_aware

from ..models import Bin

"""
custom mixin to handle all filtering by query_params for IFCB Datasets
"""
class DatasetFiltersMixin:

    def handle_query_param_filters(self, queryset):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get("smoothing_factor", 1)
        try:
            earliest_bin = Bin.objects.earliest()
        except Bin.DoesNotExist:
            return queryset

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        else:
            start_date_obj = earliest_bin.sample_time

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
        else:
            end_date_obj = timezone.now()

        # Only want to get all Bin data is this is a detail view or filtered by date
        if start_date or end_date:
            # if "seaonsal" filter is True, need to get multiple date ranges across the time series
            if seasonal:
                date_ranges = []
                year_range = [*range(start_date_obj.year, end_date_obj.year + 1)]

                for year in year_range:
                    # if exclude_month_range filter is true, need to invert the date ranges so they span the next year
                    if exclude_month_range:
                        range_start_date = make_aware(
                            datetime.datetime(
                                year, end_date_obj.month, end_date_obj.day
                            )
                        )
                        range_end_date = make_aware(
                            datetime.datetime(
                                year + 1, start_date_obj.month, start_date_obj.day
                            )
                        )
                    else:
                        range_start_date = make_aware(
                            datetime.datetime(
                                year, start_date_obj.month, start_date_obj.day
                            )
                        )
                        range_end_date = make_aware(
                            datetime.datetime(
                                year, end_date_obj.month, end_date_obj.day
                            )
                        )

                    range_dict = {
                        "year": year,
                        "start_date": range_start_date,
                        "end_date": range_end_date,
                    }
                    date_ranges.append(range_dict)

                date_q_filters = Q()
                for dr in date_ranges:
                    date_q_filters |= Q(
                        sample_time__range=(dr["start_date"], dr["end_date"])
                    )  # 'or' the Q objects together

                queryset = queryset.prefetch_related(
                    Prefetch(
                        "bins",
                        queryset=Bin.objects.filter(
                            cell_concentration_data__isnull=False
                        )
                        .filter(date_q_filters)
                        .annotate(smoothing=F("id") % smoothing_factor)
                        .filter(smoothing=0),
                    )
                )
            else:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        "bins",
                        queryset=Bin.objects.filter(
                            cell_concentration_data__isnull=False
                        )
                        .filter(sample_time__range=[start_date_obj, end_date_obj])
                        .annotate(smoothing=F("id") % smoothing_factor)
                        .filter(smoothing=0),
                    )
                )
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "bins",
                    queryset=Bin.objects.filter(cell_concentration_data__isnull=False)
                    .annotate(smoothing=F("id") % smoothing_factor)
                    .filter(smoothing=0),
                )
            )
        return queryset
