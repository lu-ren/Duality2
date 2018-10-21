import argparse
import base64
import getpass
import hashlib
import json
import math
import os
import pyperclip
import string
import sys

from git import Repo

STORE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'store/')
FILEPART = os.path.join(STORE_DIR, 'filepart')

def createRandomB64(nbytes):

    return base64.b64encode(os.urandom(nbytes)).decode('utf-8')

def getGeneratedSecret(filePath, pin, target):

    with open(filePath, 'r') as f:
        data = json.load(f)
        fileSecret = data[target] if target in data else data['default']

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

def createInitialFilePart():

    if os.path.isdir(STORE_DIR):
        print('store already exists!')
        sys.exit(1)

    os.mkdir(STORE_DIR)
    data = {'default': createRandomB64(1000)}

    with open(FILEPART, 'w') as f:
        f.write(json.dumps(data))

    print('store created successfully! Now create a PRIVATE repo and host your file secret there')

def updateFilePart(updateTarget):
    assert(os.path.isdir(STORE_DIR))

    with open(FILEPART, 'r') as f:
        data = json.load(f)
    
    data[updateTarget] = createRandomB64(1000)

    with open(FILEPART, 'w') as f:
        f.write(json.dumps(data))

    print(f'{updateTarget} updated successfully')

if __name__ == '__main__':
    
    def pullRepoStore(repoUrl):
        os.mkdir(STORE_DIR)
        repo = Repo.init(STORE_DIR)
        origin = repo.create_remote('origin', repoUrl)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)
    
    parser = argparse.ArgumentParser(description='A secret file based password generator')
    subparser = parser.add_subparsers(help='Generate secret subparser')
    parserA = subparser.add_parser('gen', help='Generate secret')
    parserA.add_argument('-t', action='store', dest='target',
            help='Target domain to generate')
    parserA.add_argument('-p', '--print', action='store_true', dest='print',
            help='Print the password to console')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', action='store_true', dest='secret',
            help='Create a secret output')
    group.add_argument('-c', action='store', dest='updateTarget',
            help='Change the password for a target domain')

    parsed = parser.parse_args()

    if parsed.secret:
        createInitialFilePart()
        sys.exit(0)

    if parsed.updateTarget:
        updateFilePart(parsed.updateTarget)
        sys.exit(0)

    if parsed.target:
        if not os.path.isdir(STORE_DIR):
            repoUrl = input('Please enter the git repo url containing the file secret: ').strip()
            pullRepoStore(repoUrl)

        pin = getpass.getpass(prompt='Enter pin: ')
        seed = getGeneratedSecret(FILEPART, pin, parsed.target)
        passwdBytes = getGeneratedPasswordBytes(seed, parsed.target)

        passwdString = mapToGeneratedPassword(passwdBytes)
        pyperclip.copy(passwdString)
        print('Password is copied to system clipboard!')

        if (parsed.print):
            print(passwdString)
