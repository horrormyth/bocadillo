# Views

In Bocadillo, views are functions that take at least a request and a response
as arguments, and mutate those objects as necessary.

Views can be asynchronous or synchronous, function-based or class-based.

## Asynchronous views

The recommended way to define views in Bocadillo is using the async/await syntax (as in the previous example). This allows you to call arbitrary async/await
Python code:

```python
from asyncio import sleep

async def find_post_content(slug: str):
    await sleep(1)  # perhaps query a database here?
    return 'My awesome post'

async def retrieve_post(req, res, slug: str):
    res.text = await find_post_content(slug)
```

## Synchronous views

Synchronous views are not supported since Bocadillo v0.8.0. All views must now be `async`, otherwise an exception is raised upon app initialisation.

## Class-based views

The previous examples were function-based views, but Bocadillo also supports
class-based views.

Class-based views are regular Python classes (there is no base `View` class).
Each HTTP method gets mapped to the corresponding method on the
class. For example, `GET` gets mapped to `.get()`,
`POST` gets mapped to `.post()`, etc.

Other than that, class-based view methods are just regular views:

```python
class Index:

    async def get(self, req, res):
        res.text = 'Classes, oh my!'
       
    async def post(self, req, res):
        res.text = 'Roger that'
```

A catch-all `.handle()` method can also be implemented to process all incoming
requests — resulting in other methods being ignored.

```python
class Index:

    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```
