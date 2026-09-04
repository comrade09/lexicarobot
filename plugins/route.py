"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

from aiohttp import web
from aiohttp.web import Request, Response

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(_request: Request) -> Response:
    return web.json_response("CodeXBotz")
