from pathlib import Path
import shutil

import pytest


@pytest.fixture(scope = 'session')
def session_monkeypatch():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope = 'session', autouse = True)
def workdir(session_monkeypatch):
    """
    Set working directory during test to where

    - test data are
    - and output files are allowed to be written.
    """
    path = Path(__file__).parent / 'workdir'
    session_monkeypatch.chdir(path)
    yield path


def delete_path_if_exists(path: Path):
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


@pytest.fixture
def outdir(workdir):
    path = workdir / 'output'
    delete_path_if_exists(path)
    yield path
    delete_path_if_exists(path)

