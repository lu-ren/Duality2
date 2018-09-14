import argparse
import base64
import hashlib
import getpass
import math
import os
import string
import sys
import pyperclip

from git import Repo

CACHE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache/')
FILEPART = os.path.join(CACHE_DIR, 'filepart')

def createFilePart(nbytes):

    return base64.b64encode(os.urandom(nbytes)).decode('utf-8')

def getGeneratedSecret(filePath, pin):

    with open(filePath, 'r') as f:
        fileSecret = f.read().strip()

    t = fileSecret + pin
    m = hashlib.sha512()
    m.update(t.encode('utf-8'))

    return m.digest()

def getGeneratedPasswordBytes(seed, target):

    return hashlib.pbkdf2_hmac('sha512', seed, target.encode('utf-8'), 10000)

def mapToGeneratedPassword(passwdBytes):

    specials = '!@#$%&*?{}'
    elements = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + specials)
    passwdLength = 16
    chunkLength = math.floor(len(passwdBytes)/passwdLength)
    values = [int.from_bytes(chunk, byteorder='big', signed=False) for chunk in chunkBytes(passwdBytes, chunkLength)]

    return ''.join([elements[values[i] % len(elements)] for i in range(len(values))])

def chunkBytes(string, length):

    return (string[0 + i: length + i] for i in range(0, len(string), length))

if __name__ == '__main__':
    
    def pullRepoCache(repoUrl):
        os.mkdir(CACHE_DIR)
        repo = Repo.init(CACHE_DIR)
        origin = repo.create_remote('origin', repoUrl)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)
    
    parser = argparse.ArgumentParser(description='A secret file based password generator')
    parser.add_argument('-t', action='store', dest='target',
            help='Target domain')
    parser.add_argument('-s', action='store_true', dest='secret',
            help='Create a secret output')
    parser.add_argument('-p', '--print', action='store_true', dest='print',
            help='Print the password to console')

    parsed = parser.parse_args()

    if not (parsed.secret or parsed.target):
        parser.print_help()
        sys.exit(1)

    if parsed.target and parsed.secret:
            parser.print_help()
            sys.exit(1)

    if parsed.secret:
        if os.path.isdir(CACHE_DIR):
            print('cache already exists!')
            sys.exit(1)
        os.mkdir(CACHE_DIR)
        with open(FILEPART, 'w') as f:
            f.write(createFilePart(1000))
        print('cache created successfully! Now create a PRIVATE repo and host your file secret there')
        sys.exit(0)

    if not os.path.isdir(CACHE_DIR):
        repoUrl = input('Please enter the git repo url containing the file secret: ').strip()
        pullRepoCache(repoUrl)

    pin = getpass.getpass(prompt='Enter pin: ')
    seed = getGeneratedSecret(FILEPART, pin)
    passwdBytes = getGeneratedPasswordBytes(seed, parsed.target)

    passwdString = mapToGeneratedPassword(passwdBytes)
    pyperclip.copy(passwdString)
    print('Password is copied to system clipboard!')

    if (parsed.print):
        print(passwdString)
