===================
Django Form Timeout
===================

Note: this application has not yet been tested in production. Use at your
own risk!

A simple application that deters users from getting around form validation by
locking them out for a period of time after a number of invalid submissions.

The typical use case is to ban attempts to login a specific user if an
incorrect password has been used too many times.

Installation
============

Add ``form_timeout`` to the ``INSTALLED_APPS`` in your project's settings
module.

Generate an augumented form using ``form_timeout.forms.form_factory``::

    from django.contrib.auth.forms import AuthenticationForm
    from form_timeout.forms import form_factory

    Form = form_factory(AuthenticationForm, 'username')

Configuration
=============

The application supports the following settings directives:

``FORM_TIMEOUT_ATTEMPTS``
``FORM_TIMEOUT_PENALTY``
