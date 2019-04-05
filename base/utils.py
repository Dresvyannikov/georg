import hashlib


def md5(filename):
    with open(filename, 'rb') as f:
        m = hashlib.md5()
        for chank in iter(lambda: f.read(4096), b""):
            m.update(chank)
        return m.hexdigest()
