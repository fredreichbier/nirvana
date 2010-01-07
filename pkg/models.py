from django.db import models
from django.contrib.auth.models import User

from nirvana.pkg.stuff import DBVersionSlugField, sign

class Package(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=128)
    author = models.ForeignKey(User)
    homepage = models.URLField(null=True, blank=True)
    category = models.ForeignKey('Category')

    def __unicode__(self):
        return self.name

    def get_authorized_variants(self, user):
        variants = []
        if user.is_authenticated():
            for permission in self.manager_permissions.filter(user=user):
                if Variant.objects.filter(slug=permission.variant_slug):
                    variants.append(permission.variant_slug)
        return variants

    def is_authorized_for_variant(self, user, variant_slug):
        if user.is_authenticated():
            if user == self.author:
                return True
            for permission in self.manager_permissions.all():
                if (permission.user == user and permission.variant_slug == variant_slug):
                    return True
        return False

class ManagerPermission(models.Model):
    user = models.ForeignKey(User)
    variant_slug = models.SlugField(max_length=50)
    package = models.ForeignKey(Package, related_name='manager_permissions')

    def __unicode__(self):
        return '%s -> %s' % (self.user, self.variant_slug)

class Version(models.Model):
    slug = DBVersionSlugField(max_length=50)
    name = models.CharField('Name', max_length=128, blank=True)
    package = models.ForeignKey('Package')
    latest = models.BooleanField('Latest version')

    def __unicode__(self):
        return '%s %s' % (self.slug, self.name)

    def make_latest(self):
        """
            mark this version as the latest available version.
            This will not save self.
        """
        for version in Version.objects.filter(package=self.package):
            if (version.latest and version != self):
                version.latest = False
                version.save()
        self.latest = True

class Variant(models.Model):
    slug = models.SlugField(max_length=50)
    name = models.CharField('Name', max_length=128, blank=True)
    version = models.ForeignKey(Version)
    usefile = models.TextField()
    checksums = models.TextField(blank=True)
    checksums_signature = models.TextField(blank=True)

    def __unicode__(self):
        return '%s %s' % (self.slug, self.name)

    def set_signature(self):
        if self.checksums:
            self.checksums_signature = sign(self.checksums)
        else:
            self.checksums_signature = ''

class Category(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name
