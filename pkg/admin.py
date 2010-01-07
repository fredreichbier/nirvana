from django.contrib import admin
from nirvana.pkg.models import Package, Version, Category, Variant, ManagerPermission

admin.site.register(ManagerPermission)
admin.site.register(Package)
admin.site.register(Version)
admin.site.register(Category)
admin.site.register(Variant)
