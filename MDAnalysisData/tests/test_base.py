# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os.path

import pytest

from MDAnalysisData import base
from MDAnalysisData import adk_equilibrium

@pytest.fixture(scope="module")
def some_text():
    return (u"Four score and seven years ago \n"
            u"our fathers brought forth on this continent, \n"
            u"a new nation, conceived in Liberty, and dedicated\n"
            u"to the proposition that all men are created equal.")

@pytest.fixture
def bunch():
    return base.Bunch(a=1, b=2)

class TestBunch(object):
    def test_getattr(self, bunch):
        assert bunch.a == 1
        assert bunch['a'] == bunch.a
        assert bunch.b == 2

    def test_missing_attr(self, bunch):
        with pytest.raises(AttributeError):
            bunch.does_not_exist

    @pytest.mark.parametrize("key,value", [
        ("a", "fortytwo"),
        ("c", -1),
        ("_hidden", None),
        ])
    def test_setattr(self, bunch, key, value):
        setattr(bunch, key, value)
        assert bunch[key] == value

    def test_dir(self, bunch):
        assert dir(bunch) == list(bunch.keys())


def test_read_description():
    descr = base._read_description("adk_equilibrium.rst")
    assert len(descr) == 1252
    assert descr.startswith(".. -*- coding: utf-8 -*-\n\n.. _`adk-equilibrium-dataset`:")

def test_sha256(tmpdir, some_text):
    filename = "address.txt"
    with tmpdir.as_cwd():
        with open(filename, "w") as txt:
            txt.write(some_text)
        checksum = base._sha256(filename)
    assert checksum == "4446bfb2ec5dedfbd981d059d6005f5144b067b392a00e3bcf98f8302ec8f765"

@pytest.mark.parametrize('data_home,location', [
    (None, os.path.expanduser("~/MDAnalysis_data")),
    ("/tmp/MDAnalysisData", "/tmp/MDAnalysisData"),
    ])
def test_get_data_home(data_home, location):
    assert base.get_data_home(data_home=data_home) == location

def test_clear_data_home(tmpdir, some_text):
    data_home_path = tmpdir.join("MDAnalysis_data_test")
    data_home = base.get_data_home(data_home=str(data_home_path))
    textfile = data_home_path.join("address.txt")
    textfile.write_text(some_text, encoding="utf-8")

    assert data_home_path.exists()  # get_data_home() should have created it
    assert data_home == str(data_home_path)
    assert textfile.exists()

    base.clear_data_home(data_home=data_home)
    assert not data_home_path.exists()  # should have been deleted
    assert not textfile.exists()        # the directory should be gone...


@pytest.fixture
def remote_topology():
    # small-ish file
    return adk_equilibrium.ARCHIVE['topology']

def test_fetch_remote(remote_topology, tmpdir):
    filename = base._fetch_remote(remote_topology, dirname=str(tmpdir))
    assert os.path.basename(filename) == remote_topology.filename
    assert os.path.dirname(filename) == str(tmpdir)