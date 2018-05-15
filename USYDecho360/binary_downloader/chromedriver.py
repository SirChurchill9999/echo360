#!/usr/bin/env python

import sys, os, stat
import shutil

CHROMEDRIVER_DOWNLOAD_LINK_ROOT = 'https://chromedriver.storage.googleapis.com'
CHROMEDRIVER_VERSION = '2.38'

def get_os_suffix():
    if 'linux' in sys.platform:
        arch = '64' if sys.maxsize > 2**32 else '32'
        if arch == '64':
            return 'linux64'
        else:
            return 'linux32'
    elif 'win32' in sys.platform:
        return 'win32'
    elif 'darwin' in sys.platform:
        return 'mac64'
    else:
        raise Exception('NON-EXISTING OS VERSION')

def get_download_link():
    os_suffix = get_os_suffix()
    filename = 'chromedriver_{0}.zip'.format(os_suffix)
    download_link = '{0}/{1}/{2}'.format(CHROMEDRIVER_DOWNLOAD_LINK_ROOT, CHROMEDRIVER_VERSION, filename)
    return download_link, filename

def get_bin_root_path():
    return '{0}/bin'.format(os.getcwd())

def get_bin():
    extension = '.exe' if 'win' in get_os_suffix() else ''
    return '{0}/chromedriver{1}'.format(get_bin_root_path(), extension)


def download():
    print('>> Downloading chrome binary file for "{0}"'.format(get_os_suffix()))
    # Download bin for this os
    import wget
    link, filename = get_download_link()
    bin_path = get_bin_root_path()
    # delete bin directory if exists
    if os.path.exists(bin_path):
        shutil.rmtree(bin_path)
    os.makedirs(bin_path)
    # remove existing binary file or folder
    wget.download(link, out='{0}/{1}'.format(bin_path, filename))
    print('\r\n>> Extracting archive file "{0}"'.format(filename))
    if sys.version_info >= (3,0): # compatibility for python 2 & 3
        shutil.unpack_archive('{0}/{1}'.format(bin_path, filename), extract_dir=bin_path)
    else:
        if '.zip' in filename:
            import zipfile
            with zipfile.ZipFile('{0}/{1}'.format(bin_path, filename), 'r') as zip:
                zip.extractall(bin_path)
        elif '.tar' in filename:
            import tarfile
            with tarfile.open('{0}/{1}'.format(bin_path, filename)) as tar:
                tar.extractall(path=bin_path)
    # Make the extracted bin executable
    st = os.stat(get_bin())
    os.chmod(get_bin(), st.st_mode | stat.S_IEXEC)
