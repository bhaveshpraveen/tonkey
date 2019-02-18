# Tonkey



> "Reinventing the wheel is great if your goal is to learn more about wheels."
> -- James Tauber

A simple web framework(kinda) that is wsgi complaint.

Made only using the Python Standard Library (exception: Twisted)

Twisted Web Server was used. So you need to pip-install twisted

```python
pip install twisted
```



### Examples

**File Structure**

├── Tonkey   
│   ──  ...   
├── app.py

**app.py**

```python
from Tonkey import Response, Router


def ola_framework(request, name, *args):
    return Response(
        r'<h1>'
        f'Welcome {name} From Tonkey'
        r'</h1>'
    )

router = Router()
router.add_route(r'/(.*)/ola/$', ola_framework)
```

Run this command from the root.

```python
PYTHONPATH=. TONKEY_APP=app twist web --wsgi Tonkey.main.application
```

You need to add the path as twisted is not added to the path automatically.

Navigate to  `http://localhost:8080/ichigo/ola/`

You should see `Welcome ichigo From Tonkey`



To use templates, use `TemplateResponse`

**app.py**

```python
from Tonkey import Response, Router, TemplateResponse


def hello_framework(request, name, *args):
    return TemplateResponse('hello_world.html', context=dict(name=name))

router = Router()
router.add_route(r'/(.*)/ola/$', ola_framework)
```

`**hello_world.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tonkey</title>
</head>
<body>
        <h1>Hello $name From Tonkey!! </h1>
</body>
</html>
```

Templating is done using the `string.Template` from python stdlib

Navigate to `http://localhost:8080/ichigo/hello/`

You should see `Hello ichigo From Tonkey!! `



The query strings from the URL can be captured in the following manner.

```python
from Tonkey import Response, Router, TemplateResponse


def hello_framework(request, *args):
    name = ','.join(request.GET.get('name', ''))
    return TemplateResponse('hello_world.html', context=dict(name=name))


router = Router()
router.add_route(r'/hello/$', hello_framework)
```

Navigate to `http://localhost:8080/hello/?name=kurosaki`

You should see `Hello kurosaki From Tonkey!! `



TODO:

- User Authentication (Done this before. Will do it again. Sigh!)
- Sessions (Need to check out)
- Other methods (post, put, patch. Actually I don't need to. I could provide a nice abstraction for those methods but all of the parameters are available as `response.environ`)
- Data layer (something as simple as using sqlite3 from stdlib)
