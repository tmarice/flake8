"""Module containing the tests for flake8.hooks."""
import os
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import flake8.hooks
from flake8.util import is_windows


def excluded(filename):
    return filename.endswith('afile.py')


class TestGitHook(unittest.TestCase):
    if is_windows:
        current_drive, ignore_tail = os.path.splitdrive(os.getcwd())
        fake_path_at_root_of_filesystem = os.path.join(current_drive,
                                                       os.path.sep,
                                                       'fake',
                                                       'tmp')
    else:
        fake_path_at_root_of_filesystem = os.path.join(os.path.sep,
                                                       'fake',
                                                       'tmp')

    @mock.patch('os.makedirs')
    @mock.patch('flake8.hooks.open', create=True)
    @mock.patch('shutil.rmtree')
    @mock.patch('tempfile.mkdtemp',
                return_value=fake_path_at_root_of_filesystem)
    @mock.patch('flake8.hooks.run',
                return_value=(None,
                              [os.path.join('foo', 'afile.py'),
                               os.path.join('foo', 'bfile.py')],
                              None))
    @mock.patch('flake8.hooks.get_style_guide')
    def test_prepends_tmp_directory_to_exclude(self, get_style_guide, run,
                                               *args):
        style_guide = get_style_guide.return_value = mock.Mock()
        style_guide.options.exclude = [os.path.join('foo', 'afile.py')]
        style_guide.options.filename = [os.path.join('foo', '*')]
        style_guide.excluded = excluded

        flake8.hooks.git_hook()

        dirname, filename = os.path.split(
            os.path.abspath(os.path.join('foo', 'bfile.py')))
        if is_windows:
            ignore_drive, dirname = os.path.splitdrive(dirname)
        tmpdir = os.path.join(self.fake_path_at_root_of_filesystem,
                              dirname[1:])
        tmpfile = os.path.join(tmpdir, 'bfile.py')
        style_guide.check_files.assert_called_once_with([tmpfile])


if __name__ == '__main__':
    unittest.main()
