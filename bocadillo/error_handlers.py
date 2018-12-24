"""Built-in error handlers."""
import traceback
from functools import wraps
from typing import Callable, Optional, Awaitable

from .exceptions import HTTPError
from .request import Request
from .response import Response


async def error_to_html(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.html = f"<h1>{exc}</h1>"


async def error_to_media(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.media = {"error": str(exc), "status": exc.status_code}


async def error_to_text(req, res, exc: HTTPError):
    res.status_code = exc.status_code
    res.text = str(exc)


ErrorHandler = Callable[[Request, Response, Exception], Awaitable[None]]
