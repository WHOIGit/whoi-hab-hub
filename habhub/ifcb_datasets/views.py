import requests
import csv
import datetime

from django.shortcuts import render
from django.contrib.gis.geos import Point

from .models import *

# Views to access IFCB Dashboard
# -------------------------------
