import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from celery import shared_task
from django.contrib.sites.models import Site
from rest_framework.reverse import reverse


@shared_task(time_limit=84600, soft_time_limit=84600)
def prewarm_api_cache():
    # periodic task to hit api endpoints to prewarm the cache
    domain = Site.objects.get_current().domain
    print(domain)
    # warm the IFCB spatial grid views
    page = reverse("api_v1:ifcb-spatial-grid-list")
    print(page)
    api_url = f"https://{domain}{page}"
    print(api_url)
    # match default start date from the React frontend app
    start_date_obj = datetime.now() - relativedelta(years=5)
    start_date = start_date_obj.strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "seasonal": "false",
        "smoothing_factor": 4,
        "exclude_month_range": "false",
        "grid_level": 0.5,
    }

    response = requests.get(api_url, params=params)
    print(response.status_code, response.url)
