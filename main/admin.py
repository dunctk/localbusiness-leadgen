from django.contrib import admin
import main.models

# Register your models here.
admin.site.register(main.models.OutscraperTask)


@admin.register(main.models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_latitude', 'get_longitude', 'website')

    def get_latitude(self, obj):
        # Assumes that location is a PointField.
        if obj.location:
            return obj.location.y  # In GEOSGeometry, y coordinate is latitude.
        return None
    get_latitude.short_description = "Latitude"

    def get_longitude(self, obj):
        # Assumes that location is a PointField.
        if obj.location:
            return obj.location.x  # In GEOSGeometry, x coordinate is longitude.
        return None
    get_longitude.short_description = "Longitude"


@admin.register(main.models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstname', 'lastname', 'ps_text')  # Adjust fields as per your existing setup.
    readonly_fields = ('ps_text',)  # Add as read-only since it's calculated and not directly editable

    def get_readonly_fields(self, request, obj=None):
        # Method for dynamically setting read-only fields.
        readonly_fields = super(ContactAdmin, self).get_readonly_fields(request, obj)
        return readonly_fields + ('ps_text',)