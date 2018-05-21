"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

import os
import sys
import logging

__version__ = '0.1'
__PLUGINS__ = "plugins/"


def config_logging():
    logging.basicConfig(filename="%s.log" % os.path.basename(sys.argv[0]), level=logging.DEBUG,
                        format="[%(asctime)s] %(levelname)-8s %(message)s", datefmt='%H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.debug('Starting..')


def load_plugins():
    imported_plugins = []
    plugins = os.listdir('plugins')
    for plugin in plugins:
        if plugin != "baseplugin.py" and plugin != "__pycache__":
            exec("from plugins import "+plugin.split(".")[0])
            imported_plugins.append(plugin.split(".")[0])
    logging.debug(os.listdir('plugins'))
    logging.debug(imported_plugins)
    return imported_plugins


def main():
    config_logging()
    plugins = load_plugins()


if __name__ == '__main__':
    main()
