import hashlib


def get_file_sha1(file_path):
    # adapted from https://www.pythoncentral.io/hashing-files-with-python/
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file_path, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def get_string_sha1(string_to_hash):
    hash_object = hashlib.sha1(string_to_hash.encode())
    return hash_object.hexdigest()
