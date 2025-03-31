Installation
============

Installation Steps
------------------

1. **Install the package:**

   .. code-block:: bash

       pip install django-altcha

2. **Add to `INSTALLED_APPS`:**

   Update your Django project's `settings.py`:

   .. code-block:: python

       INSTALLED_APPS = [
           # Other installed apps
           "django_altcha",
       ]

Usage
-----

Adding the CAPTCHA Field to Your Form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add the Altcha CAPTCHA field to a Django form, import `AltchaField` and add it to
your form definition:

.. code-block:: python

   from django import forms
   from django_altcha import AltchaField

   class MyForm(forms.Form):
       captcha = AltchaField()

Configuration Options
---------------------

You can pass configuration options to `AltchaField` that are supported by Altcha.
These options are documented at
`Altcha's website integration guide <https://altcha.org/docs/website-integration/>`_.

Example with additional options:

.. code-block:: python

   class MyForm(forms.Form):
       captcha = AltchaField(
           floating=True,   # Enables floating behavior
           debug=True,      # Enables debug mode (for development)
           # Additional options supported by Altcha
       )
