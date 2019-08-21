import json
import logging
import pathlib

import aiohttp.web
import configargparse

import aufseher.app


def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument(
        '--port',
        type=int,
        default=80,
        env_var='AUFSEHER_PORT',
        help='port to serve on (default: %(default)s)')
    parser.add_argument('--verbose', action='store_true')
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument(
        '--config',
        metavar='FILE',
        type=pathlib.Path,
        required=True,
        env_var='AUFSEHER_CONFIG_FILE',
        help='configuration file')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.view('/lights', aufseher.app.LightsHandler)])

    app.update(config)

    all_strips = []
    for group, strips in app['strips'].items():
        for name, data in strips.items():
            all_strips.append(aufseher.app.LightStrip(group, name, **data))

    app['all_strips'] = all_strips
    aiohttp.web.run_app(app, port=args.port)


if __name__ == '__main__':
    main()
