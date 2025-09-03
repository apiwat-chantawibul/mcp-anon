import logging

from .cli import cli


if __name__ == '__main__':
    logging.basicConfig(
        format = '%(asctime)s %(name)s %(levelname)s: %(message)s',
        level = logging.INFO,
    )
    cli(prog_name = 'anon-runner')

