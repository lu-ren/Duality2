## About
Duallity2 is a simple python-based generative password manager.
It generates passwords based on three inputs: a file secret, a pin, and the url.

Generating passwords is as follows:
- Intermediate := SHA512(pin + fileSecret)
- 100,000 rounds of pdkf2_hmac(Intermediate + url)

The file secret is intended to be stored and managed in a private git repo.

In a way, the password to your git repo can be considered your master password.

## Requirements

- Python3
- GitPython
- pyperclip

## Usage


### Getting started

- Generate a file secret - `python3 duality.py -s` 
- The file secret will be found in the same directory as the script under the directory called "store".
- Create a private git repo and add the file secret. (Currently, the password manager doesn't manage the secret for you. You'll have to do that with git yourself. For instance, if you switch to a new computer, you'll want to pull the repo to the same directory as the password manager.)
- Generate a secret- `python3 duality.py gen -t google.com`. Enter your pin. The password is copied to your system clipboard. You can also print the password- `python3 duality.py gen -t google.com -p`
- To change the password for a specific url - `python3 duality.py -c google.com` (You'll want to commit and push the file secret directory to your private repo after this)


## Todo
- Integrate git commands to the script and automate the versioning process such that users do not have to enter separate git comands to manage their file secret.
