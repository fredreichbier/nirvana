from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^$', 'nirvana.pkg.views.categories'),
    (r'^admin/', include(admin.site.urls)),
    (r'^categories/$', 'nirvana.pkg.views.categories'),
    (r'^category/(?P<slug>[-\w]+)/$', 'nirvana.pkg.views.category'),
    (r'^package/new/$', 'nirvana.pkg.views.package_new'),
    (r'^package/(?P<slug>[-\w]+)/new/$', 'nirvana.pkg.views.version_new'),
    (r'^packages/(?P<slug>[-\w]+)/$', 'nirvana.pkg.views.package'),
    (r'^packages/(?P<slug>[-\w]+)/latest/$', 'nirvana.pkg.views.version', {'version_slug': None}),
    (r'^packages/(?P<slug>[-\w]+)/(?P<version_slug>[-\w.]+)/$', 'nirvana.pkg.views.version'), # TODO: fix the version regex
    (r'^packages/(?P<slug>[-\w]+)/latest/(?P<usefile>[-\w]+)\.use$', 'nirvana.pkg.views.usefile', {'version_slug': None}),
    (r'^packages/(?P<slug>[-\w]+)/(?P<version_slug>[-\w.]+)/(?P<usefile>[-\w]+)\.use$', 'nirvana.pkg.views.usefile'), # TODO: fix the version regex

    (r'^accounts/', include('registration.backends.default.urls')),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/fred/dev/ooc/nirvana/media'}), # TODO: only for development
)
