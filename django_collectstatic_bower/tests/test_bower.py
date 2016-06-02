"""Tests bower adapter"""
import os
from unittest.mock import patch, Mock

from django.test import override_settings
from nose.tools import assert_equal

from django_collectstatic_bower import bower


@patch('django_collectstatic_bower.bower.get_bower_executable_path')
@patch('subprocess.Popen')
def test_bower_subprocess(subprocess_mock, exe_path_mock):
	"""Tests that the provided bower executable is launched in a subprocess"""
	exe_path = '/path/to/bower'
	cmd = 'install'
	cwd = os.getcwd()

	exe_path_mock.return_value = exe_path
	proc_mock = Mock()
	proc_mock.configure_mock(**{
		'wait': lambda: None,
		'returncode': 0
	})
	subprocess_mock.return_value = proc_mock

	bower.bower(cmd)

	subprocess_mock.assert_called_with((exe_path, cmd), cwd=cwd)


def test_bower_get_executable():
	"""Tests that the get_bower_cmd() finds the path to the bower executable"""
	# Verify django settings override option
	with override_settings(BOWER_CMD='/override/path'):
		assert_equal(bower.get_bower_executable_path(), '/override/path')

	with override_settings():
		with patch('django_collectstatic_bower.bower.shutil.which') as which:
			which.return_value = '/discovered/path'
			assert_equal(bower.get_bower_executable_path(), '/discovered/path')


def test_bower_rc():
	"""Tests that the .bowerrc file can be parsed"""


def test_bower_get_component_path():
	"""Tests that the directory bower installs to is discovered correctly"""



