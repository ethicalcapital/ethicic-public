
Kinsta logo

Ethical Capital
Ethical Capital
/
/
Ethical Capital Public




Sloane Ortel
Sloane Ortel
Overview
Deployments
Logs
Analytics
Environment variables
Processes
Domains
Networking
Disks
Web terminal
User management
Settings
You have undeployed changes.
Deploy changes
Logs
Filter logs
Load more
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Jul 03 19:43:09
    return _bootstrap._gcd_import(name[level:], package, level)
Jul 03 19:43:09
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "", line 1204, in _gcd_import
Jul 03 19:43:09
  File "", line 1176, in _find_and_load
Jul 03 19:43:09
  File "", line 1147, in _find_and_load_unlocked
Jul 03 19:43:09
  File "", line 690, in _load_unlocked
Jul 03 19:43:09
  File "", line 940, in exec_module
Jul 03 19:43:09
  File "", line 241, in _call_with_frames_removed
Jul 03 19:43:09
  File "/app/ethicic/urls.py", line 291, in
Jul 03 19:43:09
    path('', include('public_site.urls')),
Jul 03 19:43:09
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/site-packages/django/urls/conf.py", line 39, in include
Jul 03 19:43:09
    urlconf_module = import_module(urlconf_module)
Jul 03 19:43:09
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
Jul 03 19:43:09
    return _bootstrap._gcd_import(name[level:], package, level)
Jul 03 19:43:09
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "", line 1204, in _gcd_import
Jul 03 19:43:09
  File "", line 1176, in _find_and_load
Jul 03 19:43:09
  File "", line 1147, in _find_and_load_unlocked
Jul 03 19:43:09
  File "", line 690, in _load_unlocked
Jul 03 19:43:09
  File "", line 940, in exec_module
Jul 03 19:43:09
  File "", line 241, in _call_with_frames_removed
Jul 03 19:43:09
  File "/app/public_site/urls.py", line 9, in
Jul 03 19:43:09
    from .test_width import test_width_view
Jul 03 19:43:09
ModuleNotFoundError: No module named 'public_site.test_width'
Jul 03 19:43:09
Jul 03 19:43:09
During handling of the above exception, another exception occurred:
Jul 03 19:43:09
Jul 03 19:43:09
Traceback (most recent call last):
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
Jul 03 19:43:09
    response = get_response(request)
Jul 03 19:43:09
               ^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 129, in __call__
Jul 03 19:43:09
    response = response or self.get_response(request)
Jul 03 19:43:09
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^
Jul 03 19:43:09
  File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 57, in inner
Jul 03 19:43:09
    response = response_for_exception(request, exc)
