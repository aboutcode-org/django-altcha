1. Add "to INSTALLED_APPS:

INSTALLED_APPS = [
    # ...
    "django_altcha"
]

2. Add the field on your forms:

from django_altcha import AltchaField

class Form(forms.Form):
    captcha = AltchaField()

3. Configure: You can provide any configuration options available at
https://altcha.org/docs/website-integration/ such as:

class Form(forms.Form):
    captcha = AltchaField(
        floating=True,
        debug=True,
        # ...
    )
