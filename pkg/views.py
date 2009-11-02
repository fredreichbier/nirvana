from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from nirvana.pkg.models import Category, Package, Version

def categories(request):
    categories = Category.objects.all()
    return render_to_response(
            'categories.html',
            {'categories': categories},
            context_instance=RequestContext(request),
            )

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    packages = Package.objects.filter(category=category)
    return render_to_response(
            'category.html',
            {
                'category': category,
                'packages': packages,
            },
            context_instance=RequestContext(request),
            )

def package(request, slug):
    package = get_object_or_404(Package, slug=slug)
    versions = Version.objects.filter(package=package)
    return render_to_response(
            'package.html',
            {
                'package': package,
                'versions': versions,
            },
            context_instance=RequestContext(request),
            )

def version(request, slug, version_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None: # display latest version
        version = package.latest_version
    else:
        version = get_object_or_404(Version, slug=version_slug)
    return render_to_response(
            'version.html',
            {
                'package': package,
                'version': version
            },
            context_instance=RequestContext(request),
            )

def usefile(request, slug, version_slug, usefile):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None: # display latest version
        version = package.latest_version
    else:
        version = get_object_or_404(Version, slug=version_slug)
    if usefile != package.slug:
        raise Http404()
    return HttpResponse(version.usefile, mimetype='text/plain')

@login_required
def upload(request):
    return render_to_response(
            'upload.html',
            context_instance=RequestContext(request),
            )
