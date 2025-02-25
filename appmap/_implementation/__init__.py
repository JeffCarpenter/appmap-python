from . import configuration
from . import env as appmapenv
from . import event, importer, metadata, recorder
from .py_version_check import check_py_version


def initialize(**kwargs):
    check_py_version()
    appmapenv.initialize(**kwargs)
    event.initialize()
    importer.initialize()
    recorder.initialize()
    configuration.initialize()  # needs to be initialized after recorder
    metadata.initialize()


initialize()
