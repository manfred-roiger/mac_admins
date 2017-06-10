from django.contrib import admin
from .models import ComputerGroup, Computer, ComputerGroupMembership

class ComputerAdmin(admin.ModelAdmin):
    fields = ['computer_name', 'computer_id']
    search_fields = ['computer_name']
    list_display = ('computer_name', 'computer_id')

class ComputerGroupAdmin(admin.ModelAdmin):
    fields = ['group_name', 'group_id']
    search_fields = ['group_name']
    list_display = ('group_name', 'group_id')

class ComputerGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('computer', 'computer_group', 'assigned_by', 'date_assigned')
    list_filter = ['date_assigned']
    search_fields = ['computer__computer_name', 'computer_group__group_name']

admin.site.register(Computer, ComputerAdmin)
admin.site.register(ComputerGroup, ComputerGroupAdmin)
admin.site.register(ComputerGroupMembership, ComputerGroupMembershipAdmin)
