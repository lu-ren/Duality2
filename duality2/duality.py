import base64
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

    return hashlib.pbkdf2_hmac('sha512', seed, target.encode('utf-8'), 100_000)

def mapToGeneratedPassword(passwdBytes):

    specials = '!@#$%&*?{}'
    elements = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + specials)
    passwdLength = 20
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

def pullRepoStore(repoUrl):

    os.mkdir(STORE_DIR)
    repo = Repo.init(STORE_DIR)
    origin = repo.create_remote('origin', repoUrl)
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
