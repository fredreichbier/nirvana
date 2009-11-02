from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^$', 'nirvana.pkg.views.categories'),
    (r'^admin/', include(admin.site.urls)),
    (r'^upload/$', 'nirvana.pkg.views.upload'),
    (r'^categories/$', 'nirvana.pkg.views.categories'),
    (r'^category/(?P<slug>[a-zA-Z0-9-]+)/$', 'nirvana.pkg.views.category'),
    (r'^packages/(?P<slug>[a-zA-Z0-9-]+)/$', 'nirvana.pkg.views.package'),
    (r'^packages/(?P<slug>[a-zA-Z0-9-]+)/latest/$', 'nirvana.pkg.views.version', {'version_slug': None}),
    (r'^packages/(?P<slug>[a-zA-Z0-9-]+)/(?P<version_slug>[a-zA-Z0-9-.]+)/$', 'nirvana.pkg.views.version'), # TODO: fix the version regex
    (r'^packages/(?P<slug>[a-zA-Z0-9-]+)/latest/(?P<usefile>[a-zA-Z0-9-]+)\.use$', 'nirvana.pkg.views.usefile', {'version_slug': None}),
    (r'^packages/(?P<slug>[a-zA-Z0-9-]+)/(?P<version_slug>[a-zA-Z0-9-.]+)/(?P<usefile>[a-zA-Z0-9-]+)\.use$', 'nirvana.pkg.views.usefile'), # TODO: fix the version regex

    (r'^accounts/', include('registration.backends.default.urls')),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/fred/dev/ooc/nirvana/media'}), # TODO: only for development
)
