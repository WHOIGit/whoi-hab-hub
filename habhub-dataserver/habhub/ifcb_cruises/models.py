from django.db import models
from django.utils.timezone import now

# IFCB Cruise models

class Cruise(models.Model):
    cruise_name = models.CharField(max_length=100, null=False, blank=False)
    start_date = models.DateTimeField(default=now, null=False)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.cruise_name


class IFCBDatapoint(models.Model):
    cruise = models.ForeignKey(Cruise, related_name='ifcb_datapoint',
                                on_delete=models.CASCADE, null=False)
    file_name = models.CharField(max_length=100, null=False, blank=False)
    latitude = models.DecimalField(max_digits=20, decimal_places=18)
    longitude = models.DecimalField(max_digits=20, decimal_places=18)

    class Meta:
        ordering = ['file_name']

    def __str__(self):
        return '%s - %s' % (self.cruise.cruise_name, self.file_name)

    # Turn the file name into correct URL format for IFCB dashboard
    def get_ifcb_dashboard_link(self):
        file_name = self.file_name
        link_format = file_name.split('.')[0]
        dashboard_link = 'https://hablab.whoi.edu/ifcball/dashboard/https://hablab.whoi.edu:8888/ifcball/%s' % (link_format)
        return dashboard_link
