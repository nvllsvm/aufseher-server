import asyncio
import collections
import json
import logging

from tornado import httpclient, web

logging.basicConfig(level=logging.INFO)


httpclient.AsyncHTTPClient.configure(
    'tornado.curl_httpclient.CurlAsyncHTTPClient')


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


class LightsHandler(web.RequestHandler):
    def initialize(self):
        if not hasattr(self, 'client'):
            self.client = httpclient.AsyncHTTPClient()

    def prepare(self):
        auth_key = self.settings['authorization']
        try:
            if self.request.headers['Authorization'] != auth_key:
                raise ValueError
        except (KeyError, ValueError):
            raise web.HTTPError(401)

    async def put(self):
        body = json.loads(self.request.body)

        request_strips = body.get('strips', None)
        if request_strips is None:
            request_strips = self.settings['strips'].keys()
        elif isinstance(request_strips, list):
            if len(request_strips) == 0:
                raise web.HTTPError(400)
            for value in request_strips:
                if not isinstance(value, str):
                    raise web.HTTPError(400)
        else:
            raise web.HTTPError(400)

        strips = []
        for strip in self.application.all_strips:
            if strip.group in request_strips:
                strips.append(strip)

        await self.multi_request(strips, 'PUT', body)
        self.set_status(204)

    async def get(self):
        responses = await self.multi_request(self.application.all_strips,
                                             'GET')

        body = collections.defaultdict(dict)

        for strip, response in responses:
            if response.code == 200:
                body['strips'][strip.name] = response.json
            else:
                body['errors'][strip.name] = {'code': response.code,
                                              'body': response.json}
                self.set_status(500)

        self.write(body)

    async def multi_request(self, strips, *args, **kwargs):
        futures = []
        for strip in strips:
            futures.append(self.strip_request(strip, *args, **kwargs))

        results = await asyncio.gather(*futures)
        return results

    async def strip_request(self, strip, method, body=None):
        if body is not None:
            body = json.dumps(strip.build_body(body))

        response = await self.client.fetch(
            strip.url,
            method=method,
            body=body,
            connect_timeout=self.settings['http_timeout'],
            request_timeout=self.settings['http_timeout'])

        response.json = json.loads(response.body)

        return strip, response
