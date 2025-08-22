from pathlib import Path

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
    workdir = Path(__file__).parent / 'workdir'
    session_monkeypatch.chdir(workdir)
    yield workdir

