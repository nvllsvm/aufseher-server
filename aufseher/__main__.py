import logging
import os
import pathlib

from tornado import ioloop, web
import yaml

import aufseher.app

logging.basicConfig(level=logging.INFO)


def load_config():
    path = pathlib.Path(os.environ.get('CONFIG_FILE', 'config.yml'))
    return yaml.load(path.read_text())


def make_app():
    app = web.Application([
        ('/lights', aufseher.app.LightsHandler)],
        autoreload=True,
        **load_config())

    all_strips = []
    for group, strips in app.settings['strips'].items():
        for name, data in strips.items():
            all_strips.append(aufseher.app.LightStrip(group, name, **data))

    app.all_strips = all_strips

    return app


def main():
    app = make_app()
    app.listen(os.environ.get('PORT', 80))
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
