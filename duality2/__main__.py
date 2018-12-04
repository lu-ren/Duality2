import argparse
import getpass
import os
import sys

from .duality import *

def main():
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

    if hasattr(parsed, 'target') and parsed.target:
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

if __name__ == '__main__':
    main()
