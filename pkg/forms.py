from django.forms import ModelForm, BooleanField
from nirvana.pkg.models import Package, Version

class NewPackageForm(ModelForm):
    class Meta:
        model = Package
        fields = ('slug', 'name', 'homepage', 'category')

class NewVersionForm(ModelForm):
    make_latest = BooleanField(label='Make latest version', initial=True)

    class Meta:
        model = Version
        fields = ('slug', 'name', 'usefile')
        

