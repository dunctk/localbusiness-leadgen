from django.contrib import admin
import main.models

# Register your models here.
admin.site.register(main.models.OutscraperTask)
#admin.site.register(main.models.Company)
admin.site.register(main.models.Contact)


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