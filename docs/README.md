---
home: true
actionText: Get Started →
actionLink: /getting-started/
features:
- title: Simple and productive
  details: A minimal setup and carefully chosen included batteries help you solve common (and more advanced) problems in no time. 
- title: Async-first
  details: Fully embrace asynchronous programming to build next-generation web apps and services.
- title: Performant
  details: Built on Starlette and Uvicorn, the lightning-fast Python ASGI toolkit and server.
footer: MIT Licensed | Copyright © 2018-present Florimond Manca
---

## Quick start

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# api.py
import bocadillo

api = bocadillo.API()

@api.route('/')
async def index(req, res):
    # Use a template from the ./templates directory
    res.html = await api.template('index.html')

@api.route('/greet/{person}')
async def greet(req, res, person):
    res.media = {'message': f'Hi, {person}!'}

if __name__ == '__main__':
    api.run()
```

Launch:

```bash
python api.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? Head to our [Get Started](./getting-started/README.md) guide!
