from django.db import models
from django.contrib.auth.models import User

from nirvana.pkg.stuff import DBVersionSlugField

class Package(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=128)
    author = models.ForeignKey(User)
    homepage = models.URLField(null=True, blank=True)
    latest_version = models.OneToOneField('Version', related_name='package_something', null=True, blank=True)
    category = models.ForeignKey('Category')

    def __unicode__(self):
        return self.name

class Version(models.Model):
    slug = DBVersionSlugField(max_length=50)
    name = models.CharField(max_length=128)
    package = models.ForeignKey('Package')
    usefile = models.TextField()

    def __unicode__(self):
        return '%s %s' % (self.slug, self.name)

class Category(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name
