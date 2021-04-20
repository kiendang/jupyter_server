from importlib_metadata import entry_points
from pathlib import Path
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory

import importlib
import sys
import venv

import pytest

from jupyter_server.utils import get_client_schema_files


# Adapted from https://github.com/jasongrout/jupyter_core/blob/0310f4a199ba7da60abc54bd9115f7da9a9cec25/examples/scale/template/setup.py # noqa
setup_py_content = """
from setuptools import setup


name = 'eventlog_client'
setup(
  name=name,
  version="1.0.0",
  packages=[name],
  include_package_data=True,
  entry_points= {
    'jupyter_telemetry': [
      f'{name}.sample_entry_point = {name}:JUPYTER_TELEMETRY_SCHEMAS'
    ]
  }
)
"""


example_schema_json = """

"""

example_schema_yaml = """
"""


PACKAGE_NAME = 'eventlog_client'


def create_pkg(pkg_dir):
    module_dir = pkg_dir / PACKAGE_NAME
    module_dir.mkdir()

    init = module_dir / '__init__.py'
    init.write_text(f"JUPYTER_TELEMETRY_SCHEMAS = ['{PACKAGE_NAME}']")

    schema_dir = module_dir / 'schemas'
    schema_dir.mkdir()
    (schema_dir / '__init__.py').touch()
    (schema_dir / 'schema.yaml').write_text(example_schema_yaml)
    (schema_dir / 'scheam.json').write_text(example_schema_json)

    setup_py_path = pkg_dir / 'setup.py'
    setup_py_path.write_text(setup_py_content)

    return {
        'setup_py': setup_py_path,
        'name': pkg_dir.name,
        'pkg_dir': pkg_dir
    }


def install_pkg(pkg_dir, env_dir):
    get_pkg_install_path = (
        f"import inspect\n"
        f"import {PACKAGE_NAME}\n"
        f"from pathlib import Path\n"
        f"print(Path(inspect.getfile({PACKAGE_NAME})).parent.parent)"
    )

    env_builder = venv.EnvBuilder(with_pip=True)
    env_builder.create(env_dir)
    env = env_builder.ensure_directories(env_dir)

    check_call([env.env_exe, '-m', 'pip', 'install', pkg_dir])
    res = check_output([env.env_exe, '-c', get_pkg_install_path], encoding='UTF-8').strip()
    print(res)

    return res


@pytest.fixture
def client_pkg(tmp_path_factory):
    pkg_dir = tmp_path_factory.mktemp('packages')
    env_dir = tmp_path_factory.mktemp('env')

    create_pkg(pkg_dir)
    install_pkgs_dir = install_pkg(pkg_dir, env_dir)

    sys.path.append(install_pkgs_dir)
    yield install_pkgs_dir
    sys.path.remove(install_pkgs_dir)


def test_client_pkg(client_pkg):
    print(client_pkg)
    import eventlog_client # noqa
    print(list(entry_points()))
    print(entry_points().get('jupyter_telemetry', 'nnnnnoooooo'))
