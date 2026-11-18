import calendar
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone


def same_day_in_year(date, year):
    # the month/day of date in another year, Feb 29 becomes Feb 28 in other years
    day = min(date.day, calendar.monthrange(year, date.month)[1])
    return datetime.date(year, date.month, day)


def get_seasonal_ranges(start_date, end_date, exclude_month_range=False):
    # the "seasonal" date ranges for each year from start_date to end_date. The
    # season runs from start_date's month/day to end_date's month/day, or the rest
    # of the year between them if exclude_month_range is True. Seasons can span the
    # new year, ex: Nov-Feb. Ranges outside start_date - end_date are clipped by
    # the date range filter.
    season_start, season_end = start_date, end_date
    if exclude_month_range:
        season_start, season_end = end_date, start_date
    spans_new_year = (season_end.month, season_end.day) < (
        season_start.month, season_start.day
    )
    ranges = []
    for year in range(start_date.year - 1, end_date.year + 1):
        range_start = same_day_in_year(season_start, year)
        range_end = same_day_in_year(season_end, year + spans_new_year)
        ranges.append({"gte": range_start.isoformat(), "lte": range_end.isoformat()})
    return ranges


class ScoresFiltersMixin:
    """
    custom mixin to handle all filtering by query_params for IFCB Scores from AWS Opensearch
    """

    # date range to use if the start_date param isn't set
    default_date_range = relativedelta(years=1)

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
            start_date_obj = timezone.now() - self.default_date_range

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date_obj = timezone.now()

        if end_date_obj < start_date_obj:
            # check if end_date is BEFORE start_date. Invalid option, so reset to no results
            end_date_obj = start_date_obj

        # date filtering
        date_query = {
            "range": {
                "sampleTime": {
                    "gte": start_date_obj.isoformat(),
                    "lte": end_date_obj.isoformat(),
                }
            }
        }
        # if "seasonal" filter is True, only return the same part of each year
        # in the date range, ex: May-June for every year from 2020 to 2026
        if seasonal and (start_date or end_date):
            date_query = {
                "bool": {
                    "filter": [date_query],
                    "should": [
                        {"range": {"sampleTime": season}}
                        for season in get_seasonal_ranges(
                            start_date_obj, end_date_obj, exclude_month_range
                        )
                    ],
                    "minimum_should_match": 1,
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
