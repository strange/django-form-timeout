import datetime
import hashlib

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext as _

ALLOWED_ATTEMPTS = getattr(settings, 'FORM_TIMEOUT_ATTEMPTS', 5)
TIMEOUT_PENTALTY = getattr(settings, 'FORM_TIMEOUT_PENALTY', 60)

def form_factory(form_class, field_name):
    """Return a subclass of `form_class` that records and manages failed form
    validations.
    
    The superclass' clean-method is wrapped in a method that listens for a
    ``forms.ValidationError``. If validation fails a failed attempt will be
    recorded in the cache backend using the value of `field_name` as key. If
    the number of failed attempts exceeds ``settings.FORM_TIMEOUT_ATTEMPTS``
    the form will refuse to validate (for the value corresponding to
    `field_name`) until ``settings.FORM_TIMEOUT_PENALTY`` seconds have passed.

    """
    class Form(form_class):
        def clean(self):
            value = self.cleaned_data.get(field_name)
            if not value:
                return super(Form, self).clean()

            # Save a little overhead by computing the current time once
            # for timeout checks and recorded attempts.
            now = datetime.datetime.now()

            # Generate a cache-key from the value of field we're recording
            # failed attempts for.
            key = generate_cache_key(value)

            record = get_recoreded_attempts(key)
            record = check_recorded_attempts(key, now, record)

            try:
                cleaned_data = super(Form, self).clean()
                # The super-form did not raise any validation errors. Reset
                # the attempt count for key.
                reset_recorded_attempts(key)
                return cleaned_data
            except forms.ValidationError:
                # Record failed validation.
                record_attempt(key, now, record)
                raise
    return Form

def generate_cache_key(value):
    """Return a cache-safe hashed key based on `value`."""
    # TODO: The cache-key prefix should be customizable.
    value = 'FORM_TIMEOUT_%s' % value
    # Replace unsupported characters from the value. This is not collision
    # safe.
    value = ''.join(map(lambda v: ord(v) >= 33 and '_' or v, value))
    return hashlib.md5(value).hexdigest()

_record_cache = {}
def get_recoreded_attempts(key, record_cache=_record_cache):
    """Return record cached by `key`. Default to an empty dictionary if no
    record was found.
    
    """
    if not key in _record_cache.keys():
        record_cache[key] = cache.get(key, {})
    return record_cache[key]

def reset_recorded_attempts(key, record_cache=_record_cache):
    """Reset the count of failed attempts recorded by `key`."""
    if key in record_cache.keys():
        del(record_cache[key])
    cache.delete(key)

def check_recorded_attempts(key, now, record={}):
    """Raise a ``forms.ValidationError`` if the number of attempts since the
    last successful attempt -- or since the last served penalty -- exceeds
    ``settings.FORM_TIMEOUT_ATTEMPTS`` and the number of seconds since the
    last attempt falls behind ``settings.FORM_TIMEOUT_PENALTY``.

    The `record` supplied as an argument is always returned by this function.
    If the penalty has been served the record is reset and an empty dict is
    returned.
    
    """
    if not record:
        # The record is an empty dict -- nothing has been recorded for the
        # given key in the cache backend.
        return record

    if record['attempts'] >= ALLOWED_ATTEMPTS:
        if (now - record['last_attempt']).seconds > TIMEOUT_PENTALTY:
            # The penalty has been served -- reset the lockout.
            reset_recorded_attempts(key)
            record = {}
        else:
            interpolation_args = {
                'penalty': TIMEOUT_PENTALTY,
                'allowed_attemps': ALLOWED_ATTEMPTS,
            }
            raise forms.ValidationError(_(("Too many failed login attempts. "
                                           "Please try again in %(penalty)s "
                                           "seconds.") % interpolation_args))
    return record

def record_attempt(key, now, record={}):
    """Update `record` by increasing the number of attempts by one and setting
    the time of the last attempt to `now`. Store the updated dict in the cache
    backend at `key`.
    
    """
    if record:
        attempts = record['attempts']
    else:
        attempts = 0

    record['attempts'] = attempts + 1
    record['last_attempt'] = now

    cache.set(key, record)
