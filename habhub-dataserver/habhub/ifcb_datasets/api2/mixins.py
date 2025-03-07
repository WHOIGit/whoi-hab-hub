import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch, F, Q, ExpressionWrapper, CharField
from django.utils import timezone
from django.utils.timezone import make_aware


class ScoresFiltersMixin:
    """
    custom mixin to handle all filtering by query_params for IFCB Scores from AWS Opensearch
    """

    def handle_query_param_filters(self):
        species = self.request.query_params.get("species", None)
        dataset_id = self.request.query_params.get("dataset_id", None)
        model_id = self.request.query_params.get("model_id", None)
        # score threshold
        score_gte = self.request.query_params.get("score_gte", None)
        # date parameters
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get("smoothing_factor", 1)
        bbox_nw = self.request.query_params.get("bbox_nw", None)
        bbox_ne = self.request.query_params.get("bbox_ne", None)
        bbox_sw = self.request.query_params.get("bbox_sw", None)
        bbox_se = self.request.query_params.get("bbox_se", None)
        limit_start_date = self.request.query_params.get("limit_start_date", None)
        # parameter to paginate Open Search results
        search_after = self.request.query_params.get("search_after", None)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_obj = timezone.now() - relativedelta(years=1)

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
        # date filtering
        date_query = {
            "range": {
                "sampleTime": {
                    "gte": start_date_obj.isoformat(),
                    "lte": end_date_obj.isoformat(),
                }
            }
        }

        # score filtering
        score_query = {
            "range": {
                "score": {
                    "gte": score_gte,
                }
            }
        }

        # species filtering
        if species:
            species_list = species.split(",")
            species_query = {"terms": {"species": species_list}}

        # dataset filtering
        if dataset_id:
            dataset_list = dataset_id.split(",")
            dataset_query = {"terms": {"datasetId": dataset_list}}

        # dataset filtering
        if model_id:
            model_list = model_id.split(",")
            model_query = {"terms": {"modelId": model_list}}

        # bounding box geo filtering
        if bbox_sw and bbox_ne:
            bottom_left = bbox_sw.split(",")
            bottom_left = [round(float(i), 2) for i in bottom_left]
            top_right = bbox_ne.split(",")
            top_right = [round(float(i), 2) for i in top_right]
            bbox_query = {
                "geo_bounding_box": {
                    "point": {"bottom_left": bottom_left, "top_right": top_right}
                }
            }

        # build the Elastic Search "must" array
        must_array = [date_query]
        must_array.append(species_query) if species else False
        must_array.append(dataset_query) if dataset_id else False
        must_array.append(model_query) if model_id else False
        must_array.append(score_query) if score_gte else False
        # build the ES filter array
        filter_obj = bbox_query if bbox_sw and bbox_ne else False
        # build the ES bool object
        bool = {"must": must_array}
        if filter_obj:
            bool["filter"] = filter_obj

        query = {
            "query": {"bool": bool},
            # "size": 10000,
            "track_total_hits": True,
        }

        # add pagination if search_after exists
        if search_after:
            search_after = search_after.split(",")
            query["search_after"] = search_after
        print(query)
        return query
