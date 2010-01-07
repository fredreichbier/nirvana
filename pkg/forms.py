from django.forms import ModelForm, BooleanField, ChoiceField, ValidationError
from django.forms.models import modelformset_factory
from nirvana.pkg.models import Package, Version, Category, Variant, ManagerPermission

class NewPackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ('slug', 'name', 'homepage', 'category')

class EditPackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ('name', 'homepage', 'category') # Sorry man, can't change the slug.

class NewCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('slug', 'name')

class NewVersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ('slug', 'name', 'latest')

EditVersionForm = NewVersionForm

class NewVariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = ('slug', 'name', 'usefile', 'checksums')

    def clean_slug(self):
        if not self.package.is_authorized_for_variant(self.request.user, self.cleaned_data['slug']):
            raise ValidationError('You are not authorized to edit / create this variant.')
        return self.cleaned_data['slug']

EditVariantForm = NewVariantForm

ManagerPermissionFormSet = modelformset_factory(ManagerPermission, exclude=('package',), can_delete=True)
