"""
>>> key = generate_cache_key('Some random string')
>>> len(key)
32

>>> from django.contrib.auth.forms import AuthenticationForm
>>> Form = form_factory(AuthenticationForm, 'username')
>>> data = { 'username': 'xxx', 'password': 'yyy' }
>>> errors = []
>>> attempts = ALLOWED_ATTEMPTS + 1
>>> for i in range(0, attempts):
...    form = Form(data=data)
...    if not form.is_valid():
...        errors.append(form.errors)
>>> len(errors) == attempts
True
>>> len(set(map(str, errors)))
2

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
