import asyncio
import os
import threading
from typing import List, Optional

from aiohttp import web, WSMsgType

PORT = 8888


class Server(threading.Thread):
    def __init__(self, directory: str):
        super().__init__()
        self.dir = directory
        self.websockets: List[web.WebSocketResponse] = []
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.message = ''

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        app = web.Application()
        app.add_routes([web.get('/', self.handle), web.get('/ws', self.ws_handle)])
        web.run_app(app, port=PORT)

    async def handle(self, request: web.Request):
        return web.FileResponse(os.path.join(self.dir, 'index.html'))

    async def ws_handle(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        print('Websocket connected', request.host)

        self.websockets.append(ws)

        await ws.send_str(self.message)  # immediately send cached message

        async for msg in ws:
            if msg.type == WSMsgType.ERROR:
                print('Websocket closed with exception %s' % ws.exception())

        self.websockets.remove(ws)

        print('Websocket disconnected', request.host)

        return ws

    def send(self, message: str):
        self.message = message  # cache the message

        if not self.loop:
            return

        # https://github.com/aio-libs/aiohttp/issues/2974
        for ws in self.websockets:
            asyncio.run_coroutine_threadsafe(ws.send_str(message), self.loop)
