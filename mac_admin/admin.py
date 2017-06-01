from django.contrib import admin
from .models import ComputerGroup, Computer, ComputerGroupMembership

admin.site.register(Computer)
admin.site.register(ComputerGroup)
admin.site.register(ComputerGroupMembership)
