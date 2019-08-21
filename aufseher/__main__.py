import json
import logging
import os
import pathlib

import aiohttp.web

import aufseher.app

logging.basicConfig(level=logging.INFO)

CONFIG_PATH = pathlib.Path(os.environ.get('CONFIG_FILE', 'config.json'))


def main():
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.view('/lights', aufseher.app.LightsHandler)])

    app.update(json.loads(CONFIG_PATH.read_text()))

    all_strips = []
    for group, strips in app['strips'].items():
        for name, data in strips.items():
            all_strips.append(aufseher.app.LightStrip(group, name, **data))

    app['all_strips'] = all_strips
    aiohttp.web.run_app(app, port=os.environ.get('PORT', 80))


if __name__ == '__main__':
    main()
