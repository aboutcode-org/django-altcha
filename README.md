# Django Altcha

**Django Altcha** is a Django library that provides easy integration of Altcha CAPTCHA
into your Django forms, enhancing user verification with configurable options.

## Installation

1. **Install the package:**

   ```bash
   pip install django-altcha
   ```

2. **Add to `INSTALLED_APPS`:**

   Update your Django project's `settings.py`:

   ```python
   INSTALLED_APPS = [
       # Other installed apps
       "django_altcha",
   ]
   ```

## Usage

### Adding the CAPTCHA Field to Your Form

To add the Altcha CAPTCHA field to a Django form, import `AltchaField` and add it to
your form definition:

```python
from django import forms
from django_altcha import AltchaField

class MyForm(forms.Form):
    captcha = AltchaField()
```

## Configuration Options

You can pass configuration options to `AltchaField` that are supported by Altcha.
These options are documented at
[Altcha's website integration guide](https://altcha.org/docs/website-integration/).

### Example with additional options:

```python
class MyForm(forms.Form):
    captcha = AltchaField(
        floating=True,   # Enables floating behavior
        debug=True,      # Enables debug mode (for development)
        # Additional options supported by Altcha
    )
```

## Contributing

We welcome contributions to improve this library.
Feel free to submit issues or pull requests!

## License

This project is licensed under the **MIT License**.
See the [LICENSE](./LICENSE) file for details.
