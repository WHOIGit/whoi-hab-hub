import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch, F, Q, ExpressionWrapper, CharField
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.gis.geos import Polygon

from ..models import Bin


class BinFiltersMixin:
    """
    custom mixin to handle all filtering by query_params for IFCB Bins
    """

    def handle_query_param_filters(self, queryset):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get("smoothing_factor", 1)
        bbox_sw = self.request.query_params.get("bbox_sw", None)
        bbox_ne = self.request.query_params.get("bbox_ne", None)
        limit_start_date = self.request.query_params.get("limit_start_date", None)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_obj = timezone.now() - relativedelta(years=1)

        print("LIMIT", limit_start_date)
        if limit_start_date:
            # if limit_start_date param exists, limit results to specified range

            limit_start_date_obj = datetime.datetime.strptime(
                limit_start_date, "%Y-%m-%d"
            ).date()

            if limit_start_date_obj > start_date_obj:
                start_date_obj = limit_start_date_obj
                print(start_date_obj, limit_start_date_obj)

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date_obj = timezone.now()

        if end_date_obj < start_date_obj:
            # check if end_date is BEFORE start_date. Invalid option, so reset to no results
            end_date_obj = start_date_obj

        # create empty Q objects to handle conditional filtering
        date_q_filters = Q()

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
                print("RANGES", date_ranges)
                for dr in date_ranges:
                    date_q_filters |= Q(
                        sample_time__range=(dr["start_date"], dr["end_date"])
                    )  # 'or' the Q objects together
            else:
                date_q_filters |= Q(sample_time__range=([start_date_obj, end_date_obj]))

        queryset = (
            queryset.filter(date_q_filters)
            .annotate(
                smoothing=ExpressionWrapper(
                    F("id") % smoothing_factor, output_field=CharField()
                )
            )
            .filter(smoothing=0)
        )

        if bbox_sw and bbox_ne:
            bbox_sw = bbox_sw.split(",")
            bbox_ne = bbox_ne.split(",")
            poly_bbox = Polygon.from_bbox(bbox_sw + bbox_ne)
            queryset = queryset.filter(geom__within=poly_bbox)

        return queryset


class DatasetFiltersMixin:
    """
    custom mixin to handle all filtering by query_params for IFCB Datasets
    """

    def handle_query_param_filters(self, queryset):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get("smoothing_factor", 1)
        bbox_sw = self.request.query_params.get("bbox_sw", None)
        bbox_ne = self.request.query_params.get("bbox_ne", None)
        fixed_locations = self.request.query_params.get("fixed_locations", False)
        limit_start_date = self.request.query_params.get("limit_start_date", None)

        # limit results to only fixed locations for HABHub map
        if fixed_locations:
            queryset = queryset.filter(fixed_location=True)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_obj = timezone.now() - relativedelta(years=1)

        if limit_start_date:
            # if limit_start_date param exists, limit results to specified range

            limit_start_date_obj = datetime.datetime.strptime(
                limit_start_date, "%Y-%m-%d"
            ).date()

            if limit_start_date_obj > start_date_obj:
                start_date_obj = limit_start_date_obj

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date_obj = timezone.now()

        if end_date_obj < start_date_obj:
            # check if end_date is BEFORE start_date. Invalid option, so reset to no results
            end_date_obj = start_date_obj

        # create empty Q objects to handle conditional filtering
        date_q_filters = Q()
        # geo_q_filters = Q()

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

                for dr in date_ranges:
                    date_q_filters |= Q(
                        sample_time__range=(dr["start_date"], dr["end_date"])
                    )  # 'or' the Q objects together
            else:
                date_q_filters |= Q(sample_time__range=([start_date_obj, end_date_obj]))

        queryset = queryset.prefetch_related(
            Prefetch(
                "bins",
                queryset=Bin.objects.filter(cell_concentration_data__isnull=False)
                .filter(date_q_filters)
                .annotate(
                    smoothing=ExpressionWrapper(
                        F("id") % smoothing_factor, output_field=CharField()
                    )
                )
                .filter(smoothing=0),
            )
        )
        """
        if not is_fixed_location:
            queryset = queryset.add_bins_geo_extent(date_q_filters)
        """
        return queryset
