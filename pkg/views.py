from django.http import HttpResponse, Http404
from django.core import serializers, urlresolvers
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from nirvana.pkg.models import Category, Package, Version
from nirvana.pkg.forms import NewPackageForm, NewVersionForm, NewCategoryForm
from nirvana.pkg.stuff import json_view

def categories(request):
    categories = Category.objects.all()
    return render_to_response(
            'pkg/categories.html',
            {'categories': categories},
            context_instance=RequestContext(request),
            )

def category(request, slug):
    if slug == 'my': # special pseudo-category containing my packages
        if request.user.is_authenticated():
            packages = Package.objects.filter(author=request.user)
        else:
            # Unauthenticated users should not visit this site. However,
            # we'll just display an empty list.
            packages = []
        category_name = 'my packages'
    else:
        category = get_object_or_404(Category, slug=slug)
        packages = Package.objects.filter(category=category)
        category_name = category.name
    return render_to_response(
            'pkg/category.html',
            {
                'category_name': category_name,
                'packages': packages,
            },
            context_instance=RequestContext(request),
            )

def package(request, slug):
    package = get_object_or_404(Package, slug=slug)
    versions = Version.objects.filter(package=package)
    return render_to_response(
            'pkg/package.html',
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
            'pkg/version.html',
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
        version = get_object_or_404(Version, package=package, slug=version_slug)
    if usefile != package.slug:
        raise Http404()
    return HttpResponse(version.usefile, mimetype='text/plain')

@login_required
def package_new(request):
    if request.method == 'POST':
        form = NewPackageForm(request.POST)
        if form.is_valid():
            # uuuhuhu get an object ... 
            package = form.save(commit=False)
            # ... but set the author ...
            package.author = request.user
            # ... and save then.
            package.save()
            return redirect('nirvana.pkg.views.package', slug=package.slug)
    else:
        form = NewPackageForm()
    # if it's invalid or initial, display it.
    return render_to_response(
            'pkg/package_new.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request),
            )

@login_required
def category_new(request):
    if request.method == 'POST':
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            # do it.
            category = form.save(commit=True)
            return redirect('nirvana.pkg.views.category', slug=category.slug)
    else:
        form = NewCategoryForm()
    # if it's invalid or initial, display it.
    return render_to_response(
            'pkg/category_new.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request),
            )

@login_required
def version_new(request, slug):
    package = get_object_or_404(Package, slug=slug)
    if request.user != package.author:
        # oh oh! hacker! let's confuse him with a 404.
        raise Http404()
    else:
        if request.method == 'POST':
            form = NewVersionForm(request.POST)
            if form.is_valid():
                # TODO: only allow one package/slug combination
                # get object, save package
                version = form.save(commit=False)
                version.package = package
                version.save()
                # should it be the new latest version?
                if form.cleaned_data['make_latest']:
                    package.latest_version = version
                    package.save()
                # TODO: check version slug
                return redirect('nirvana.pkg.views.version', slug=package.slug, version_slug=version.slug)
        else:
            form = NewVersionForm()
        # if it's invalid or initial, display it.
        return render_to_response(
                'pkg/version_new.html',
                {
                    'form': form,
                },
                context_instance=RequestContext(request),
                )

def _get_type(request, choices):
    t = request.GET.get('type', choices[0])
    if t not in choices:
        raise Http404("Unknown type: %s" % t)
    return t

# API

@json_view
def api_categories(request):
    type = _get_type(request, ('contents', 'details'))
    if type == 'contents':
        return dict((c.slug, c.name) for c in Category.objects.all())
    else:
        categories = [category.slug for category in Category.objects.all()]
        return {'categories': categories}

@json_view
def api_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    packages = Package.objects.filter(category=category)
    type = _get_type(request, ('contents', 'details'))
    if type == 'contents':
        return dict((package.slug, package.name) for package in packages)
    else:
        return {
            'slug': category.slug,
            'name': category.name,
            'packages': [p.slug for p in packages]
        }

@json_view
def api_package(request, slug):
    package = get_object_or_404(Package, slug=slug)
    versions = Version.objects.filter(package=package)
    type = _get_type(request, ('contents', 'details'))
    if type == 'contents':
        return dict((v.slug, v.name) for v in versions)
    else:
        return {
                'slug': package.slug,
                'name': package.name,
                'author': package.author.username,
                'homepage': package.homepage,
                'latest_version': package.latest_version.slug,
                'category': package.category.slug,
                'versions': [v.slug for v in versions]
        }

@json_view
def api_version(request, slug, version_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None:
        version = package.latest_version
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    return {
            'slug': version.slug,
            'name': version.name,
            'package': version.package.slug,
            'usefile': urlresolvers.reverse('nirvana.pkg.views.usefile',
                kwargs={'slug': slug, 'version_slug': version_slug, 'usefile': slug},
            )
        }
