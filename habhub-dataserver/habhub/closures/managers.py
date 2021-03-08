from django.db import models
from django.db.models import Subquery, OuterRef, Avg
from django.apps import apps

class ClosureNoticeQuerySet(models.QuerySet):

    def add_monthly_data_count(self):

        return self.annotate(timestamp=TruncMonth('effective_date')) \ # Truncate to Day and add to select list
            .values('timestamp') \  # Group By Month
            .annotate(q_count=Count('id'))  # Select the count of the grouping
