===================
Django Form Timeout
===================

A simple application that deters malicious users from messing with form
validation (think brute force attacks). Users will be locked out for a period
of time after a number of invalid form submissions.

A typical use case is to disallow users from logging in as a specific user if
an incorrect password has been entered several times.

Note: this application has not yet been tested in production (it has hardly
been tested at all really). Use at your own risk!

Installation
============

Add ``form_timeout`` to ``INSTALLED_APPS`` in your project's settings module.

Generate an augmented form using ``form_timeout.forms.form_factory``::

    from django.contrib.auth.forms import AuthenticationForm
    from form_timeout.forms import form_factory

    Form = form_factory(form_class=AuthenticationForm, form_name'username')

You should be able to use the form as usual. All failed attempts to login will
be recorded by username. If an erroneous password for a given username has been
entered more than five times the user will be locked out for 60 seconds
(default settings).

Make sure that you use a sensible ``field_name`` when you generate a form. The
cleaned value of said field will be used as a key when recording failed
attempts in the cache. Good fields are unique and can be hashed without
breaking my application.

Configuration
=============

The application supports the following settings:

``FORM_TIMEOUT_ATTEMPTS`` determines the number of attempts required to trigger
the lockout. The default value is ``5``.

``FORM_TIMEOUT_PENALTY`` specifies the number of seconds during which a user
will be locked out after the lockout has been triggered. The value is set in
seconds. The default value is ``60``.

TODO
====

* Compare time of last attempt to current time prior to checking the number of
  failed attempts. You shouldn't be presented with the error if you failed
  a few logins a week ago.
* Test! Test! Test!
* Improve documentation.
* Add more tests.
* Consider adding a few convenience hooks for common applications and Django's
  own login (you can't use a custom form).
