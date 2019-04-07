import asyncio
import collections
import logging

import aiohttp
import aiohttp.web

logging.basicConfig(level=logging.INFO)


class LightStrip:
    def __init__(self, group, name, url, colors):
        self.group = group
        self.name = name
        self.url = url
        self.has_white = colors == 'rgbw'

    def build_body(self, body):
        mode = body['mode']

        if mode == 'rainbow':
            new_body = self.build_new_body(body, 'brightness', 'interval')
        elif mode == 'flash':
            new_body = self.build_new_body(
                body,
                'red', 'blue', 'green', 'white', 'brightness', 'interval')
            if new_body.get('white') == 0:
                new_body.pop('white')

        elif mode == 'color':
            new_body = self.build_new_body(
                body,
                'red', 'blue', 'green', 'white', 'brightness')
        else:
            new_body = self.build_new_body(body)

        return new_body

    def build_new_body(self, body, *keys):
        new_body = {'mode': body['mode']}

        for key in keys:
            value = body.get(key)
            if value is not None:
                new_body[key] = value

        return new_body


class LightsHandler(aiohttp.web.View):
    def check(self):
        auth_key = self.request.app['authorization']
        if self.request.headers.get('Authorization') != auth_key:
            raise aiohttp.web.HTTPBadRequest

    async def put(self):
        self.check()
        body = await self.request.json()

        request_strips = body.get('strips', None)
        if request_strips is None:
            request_strips = self.request.app['strips'].keys()
        elif isinstance(request_strips, list):
            if len(request_strips) == 0:
                raise aiohttp.web.HTTPBadRequest
            for value in request_strips:
                if not isinstance(value, str):
                    raise aiohttp.web.HTTPBadRequest
        else:
            raise aiohttp.web.HTTPBadRequest

        strips = []
        for strip in self.request.app['all_strips']:
            if strip.group in request_strips:
                strips.append(strip)

        await self.multi_request(strips, 'PUT', body)
        raise aiohttp.web.HTTPNoContent

    async def get(self):
        v = self.check()
        if v:
            return v
        responses = await self.multi_request(self.request.app['all_strips'],
                                             'GET')

        body = collections.defaultdict(dict)

        for response in responses:
            if response['status'] == 200:
                body['strips'][response['strip'].name] = response['json']
            else:
                body['errors'][response['strip'].name] = {
                    'code': response['status'],
                    'body': response['json']
                }
                raise aiohttp.web.HTTPInternalServerError

        return aiohttp.web.json_response(body)

    async def multi_request(self, strips, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[
                self.strip_request(session, strip, *args, **kwargs)
                for strip in strips
            ])
        return results

    async def strip_request(self, session, strip, method, body=None):
        kwargs = {
            'url': strip.url,
            'method': method
        }
        if body is not None:
            kwargs['json'] = strip.build_body(body)

        async with session.request(**kwargs) as response:
            d = await response.json()
            result = {
                'json': d,
                'status': response.status,
                'strip': strip
            }
        return result
