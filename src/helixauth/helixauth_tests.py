import os


if __name__ == '__main__':
    c_dir = os.path.dirname(__file__)
    nose_path = os.path.join(c_dir, '..', '..', '.venv_helix', 'bin')
    os.system('export PATH=%s:$PATH && nosetests' % nose_path)
