from django.contrib import admin
from nirvana.pkg.models import Package, Version, Category

admin.site.register(Package)
admin.site.register(Version)
admin.site.register(Category)
