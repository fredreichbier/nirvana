from django.forms import ModelForm, BooleanField, ChoiceField
from nirvana.pkg.models import Package, Version, Category

class NewPackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ('slug', 'name', 'homepage', 'category')

class EditPackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ('name', 'homepage', 'category', 'latest_version') # Sorry man, can't change the slug.

    def __init__(self, *args, **kwargs):
       super(EditPackageForm, self).__init__(*args, **kwargs)
       # only display "my versions".
       self.fields['latest_version'].queryset = Version.objects.filter(package=self.instance)

class NewCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('slug', 'name')

class NewVersionForm(ModelForm):
    make_latest = BooleanField(label='Make latest version', initial=True, required=False)

    class Meta:
        model = Version
        fields = ('slug', 'name', 'usefile')
        
class EditVersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ('slug', 'name', 'usefile')
        

