from django.http import HttpResponse, Http404
from django.core import serializers, urlresolvers
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from nirvana.pkg.models import Category, Package, Version, Variant, ManagerPermission
from nirvana.pkg.forms import EditPackageForm, NewPackageForm, EditVersionForm, NewVersionForm, NewCategoryForm, NewVariantForm, EditVariantForm, ManagerPermissionFormSet
from nirvana.pkg.stuff import json_view, get_api_token
from nirvana.pkg.usefile import parse_usefile, validate_usefile

def categories(request):
    categories = Category.objects.all()
    return render_to_response(
            'pkg/categories.html',
            {'categories': categories},
            context_instance=RequestContext(request),
            )

def welcome(request):
    return render_to_response(
            'pkg/welcome.html',
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
        version = get_object_or_404(Version, package=package, slug=version_slug)
    variants = Variant.objects.filter(version=version)
    authorized_variants = package.get_authorized_variants(request.user)
    variants_dict = dict((variant.slug, False) for variant in variants)
    for variant_slug in authorized_variants:
        variants_dict[variant_slug] = 'edit'
    return render_to_response(
            'pkg/version.html',
            {
                'package': package,
                'version': version,
                'versions': Version.objects.filter(package=package),
                'variants': variants_dict,
                'authorized': request.user.is_authenticated(),
            },
            context_instance=RequestContext(request),
            )

def variant(request, slug, version_slug, variant_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None: # display latest version
        version = package.latest_version
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    variant = get_object_or_404(Variant, version=version, slug=variant_slug)
    return render_to_response(
            'pkg/variant.html',
            {
                'package': package,
                'version': version,
                'variant': variant,
                'usefile': package.slug,
            },
            context_instance=RequestContext(request))

@login_required
def api_token(request):
    return render_to_response(
            'pkg/api_token.html',
            {
                'api_token': get_api_token(request.user),
            },
            context_instance=RequestContext(request),
            )

def _get_file_variant(slug, version_slug, variant_slug, fname):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None: # display latest version
        version = package.latest_version
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    variant = get_object_or_404(Variant, version=version, slug=variant_slug)
    if fname != package.slug:
        raise Http404()
    return variant

def usefile(request, slug, version_slug, variant_slug, usefile):
    variant = _get_file_variant(slug, version_slug, variant_slug, usefile)
    return HttpResponse(variant.usefile, mimetype='text/plain')

def checksums(request, slug, version_slug, variant_slug, checksums):
    variant = _get_file_variant(slug, version_slug, variant_slug, checksums)
    return HttpResponse(variant.checksums, mimetype='text/plain')

def checksums_signature(request, slug, version_slug, variant_slug, checksums_signature):
    variant = _get_file_variant(slug, version_slug, variant_slug, checksums_signature)
    return HttpResponse(variant.checksums_signature, mimetype='text/plain')

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
def package_edit(request, slug):
    package = get_object_or_404(Package, slug=slug)
    if request.user != package.author:
        # oh oh! hacker! let's confuse him with a 404.
        raise Http404()
    else:
        if request.method == 'POST':
            form = EditPackageForm(request.POST, instance=package)
            if form.is_valid():
                # ssssave!
                form.save()
                # TODO: check version slug
                return redirect('nirvana.pkg.views.package', slug=package.slug)
        else:
            form = EditPackageForm(instance=package)
        # if it's invalid or initial, display it.
        return render_to_response(
                'pkg/package_edit.html',
                {
                    'form': form,
                },
                context_instance=RequestContext(request),
                )

@login_required
def package_edit_managers(request, slug):
    package = get_object_or_404(Package, slug=slug)
    if request.user != package.author:
        # oh oh! hacker! let's confuse him with a 404.
        raise Http404()
    else:
        if request.method == 'POST':
            formset = ManagerPermissionFormSet(request.POST, queryset=ManagerPermission.objects.filter(package=package))
            if formset.is_valid():
                # get object, save package
                for instance in formset.save(commit=False):
                    instance.package = package
                    instance.save()
                # TODO: check version slug
                return redirect('nirvana.pkg.views.package', slug=package.slug)
        else:
            formset = ManagerPermissionFormSet(queryset=ManagerPermission.objects.filter(package=package))
        # if it's invalid or initial, display it.
        return render_to_response(
                'pkg/package_edit_managers.html',
                {
                    'formset': formset,
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
                if Version.objects.filter(slug=form.cleaned_data['slug'], package=package):
                    raise Http404("A version like this already exists.") # TODO: nicer error.
                # get object, save package
                version = form.save(commit=False)
                version.package = package
                if version.latest:
                    version.make_latest()
                version.save()
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

@login_required
def version_edit(request, slug, version_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None: # display latest version
        version = package.latest_version
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    if request.user != package.author:
        # oh oh! hacker! let's confuse him with a 404.
        raise Http404()
    else:
        if request.method == 'POST':
            form = EditVersionForm(request.POST, instance=version)
            if form.is_valid():
                if (version.slug != form.cleaned_data['slug'] and Version.objects.filter(slug=form.cleaned_data['slug'], package=package)):
                    raise Http404("A version like this already exists.") # TODO: nicer error.
                version = form.save(commit=False)
                if version.latest:
                    version.make_latest()
                version.save()
                # TODO: check version slug
                return redirect('nirvana.pkg.views.version', slug=package.slug, version_slug=version.slug)
        else:
            form = EditVersionForm(instance=version)
        # if it's invalid or initial, display it.
        return render_to_response(
                'pkg/version_edit.html',
                {
                    'form': form,
                },
                context_instance=RequestContext(request),
                )

@login_required
def variant_new(request, slug, version_slug):
    package = get_object_or_404(Package, slug=slug)
    version = get_object_or_404(Version, slug=version_slug, package=package)
    if request.method == 'POST':
        form = NewVariantForm(request.POST)
        # required for validation!
        form.package = package
        form.request = request
        if form.is_valid():
            if Variant.objects.filter(slug=form.cleaned_data['slug'], version=version):
                raise Http404("A variant like this already exists.") # TODO: nicer error.
            # get object, save package
            variant = form.save(commit=False)
            variant.version = version
            variant.set_signature()
            variant.save()
            # TODO: check usefile.
            # TODO: check version slug
            return redirect('nirvana.pkg.views.variant',
                    slug=package.slug, version_slug=version.slug, variant_slug=variant.slug)
    else:
        form = NewVariantForm()
    # if it's invalid or initial, display it.
    return render_to_response(
            'pkg/variant_new.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request),
            )

@login_required
def variant_edit(request, slug, version_slug, variant_slug):
    package = get_object_or_404(Package, slug=slug)
    version = get_object_or_404(Version, slug=version_slug, package=package)
    variant = get_object_or_404(Variant, slug=variant_slug, version=version)
    if not package.is_authorized_for_variant(request.user, variant.slug):
        raise Http404('You are not authorized to edit this variant.')
    if request.method == 'POST':
        form = EditVariantForm(request.POST, instance=variant)
        # required for validation!
        form.package = package
        form.request = request
        if form.is_valid():
            # get object, save package
            variant = form.save(commit=False)
            variant.version = version
            variant.set_signature()
            variant.save()
            # TODO: check usefile.
            # TODO: check version slug
            return redirect('nirvana.pkg.views.variant',
                    slug=package.slug, version_slug=version.slug, variant_slug=variant.slug)
    else:
        form = EditVariantForm(instance=variant)
    # if it's invalid or initial, display it.
    return render_to_response(
            'pkg/variant_edit.html',
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
    latest_version = package.latest_version
    if latest_version is not None:
        latest_version = latest_version.slug
    type = _get_type(request, ('contents', 'details'))
    if type == 'contents':
        return dict((v.slug, v.name) for v in versions)
    else:
        return {
                'slug': package.slug,
                'name': package.name,
                'author': package.author.username,
                'homepage': package.homepage,
                'latest_version': latest_version,
                'category': package.category.slug,
                'versions': [v.slug for v in versions]
        }

@json_view
def api_version(request, slug, version_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None:
        version = package.latest_version
        version_slug = 'latest'
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    variants = Variant.objects.filter(version=version)
    type = _get_type(request, ('contents', 'details'))
    if type == 'contents':
        return dict((v.slug, v.name) for v in variants)
    else:
        return {
                'slug': version.slug,
                'name': version.name,
                'package': version.package.slug,
                'latest': version.latest,
                'variants': [v.slug for v in variants]
            }

@json_view
def api_variant(request, slug, version_slug, variant_slug):
    package = get_object_or_404(Package, slug=slug)
    if version_slug is None:
        version = package.latest_version
        version_slug = 'latest'
    else:
        version = get_object_or_404(Version, package=package, slug=version_slug)
    variant = get_object_or_404(Variant, version=version, slug=variant_slug)
    return {
            'slug': variant.slug,
            'name': variant.name,
            'version': variant.version.slug,
            'usefile': urlresolvers.reverse('nirvana.pkg.views.usefile',
                kwargs={'slug': slug, 'version_slug': version_slug, 'variant_slug': variant.slug, 'usefile': slug},
            ),
            'checksums': urlresolvers.reverse('nirvana.pkg.views.checksums',
                kwargs={'slug': slug, 'version_slug': version_slug, 'variant_slug': variant.slug, 'checksums': slug},
            ),
            'checksums_signature': urlresolvers.reverse('nirvana.pkg.views.checksums_signature',
                kwargs={'slug': slug, 'version_slug': version_slug, 'variant_slug': variant.slug, 'checksums_signature': slug},
            ),
        }

@json_view
def api_submit(request):
    def _get(key):
        if key in request.POST:
            return request.POST[key]
        else:
            raise Exception('%s not found in the data!' % key)
    usefile = _get('usefile')
    username = _get('user')
    slug = _get('slug')
    api_token = _get('token')
    checksums = request.POST.get('checksums', '')
    variant_name = request.POST.get('name', '')
    # first, see if the api token is correct.
    user = get_object_or_404(User, username=username)
    if get_api_token(user) != api_token:
        raise Exception("The api token is incorrect.")
    # get & validate.
    dct = parse_usefile(usefile)
    validate_usefile(dct)
    # do we have such a package and such a version?
    package = get_object_or_404(Package, slug=slug)
    version = get_object_or_404(Version, package=package, slug=dct['Version'])
    if not package.is_authorized_for_variant(user, dct['Variant']):
        raise Exception("You are not allowed to add this variant to this package.")
    if Variant.objects.filter(slug=dct['Variant'], version=version):
        raise Exception("A variant like this already exists.")
    # yeah, we have. create a new version.
    variant = Variant(
                    slug=dct['Variant'],
                    name=variant_name,
                    version=version,
                    usefile=usefile,
                    checksums=checksums
                    )
    variant.set_signature()
    variant.save()
    return {'path':
        urlresolvers.reverse('nirvana.pkg.views.variant',
            kwargs={'slug': package.slug, 'version_slug': dct['Version'], 'variant_slug': dct['Variant']})}

@json_view
def api_authorized(request):
    def _get(key):
        if key in request.POST:
            return request.POST[key]
        else:
            raise Exception('%s not found in the data!' % key)

    username = _get('user')
    api_token = _get('token')
    package_slug = _get('package')
    version_slug = _get('version')
    variant_slug = _get('variant')

    user = get_object_or_404(User, username=username)
    if get_api_token(user) != api_token:
        raise Exception("The api token is incorrect.")

    package = get_object_or_404(Package, slug=package_slug)
    version = get_object_or_404(Version, package=package, slug=version_slug)
    return {'authorized': package.is_authorized_for_variant(user, variant_slug, True)}
