# Tlack
I've always wanted to make a terminal chat app. It has colors.

## Setup
I'm using poetry as a pm and venv, so
```bash
poetry install
poetry shell
```
then, just run as usual
```bash
python3 tlack.py COMMAND [ARGS]
```

## Options
`-h, --host` host server to join, defaults to localhost \
`-p, --port` which port to host on or join, defaults to 3000 \
`-s, --server` full server and port to join

`-n, --name` your name in the chat, default is random \
`-c, --color` which color you want your name to be, default is random

`-v, --version` show version info
