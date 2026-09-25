<p align="center">
    <b>Telegram MTProto API Framework for Python</b>
    <br />
    <br />
    <a href="https://github.com/ahmedahah4/ravengram/blob/dev/COPYING">
        <img
            src="https://img.shields.io/badge/license-LGPLv3-%23fd5216"
            alt="License"
        />
    </a>
</p>


## Ravengram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

Ravengram is a personal Pyrogram-family fork for Python, kept as a drop-in replacement for Pyrogram, with
support for the latest Telegram features including Gifts, Stories, Topics, Business Accounts, and more. It is
maintained independently so that Telegram API updates can be pulled in without waiting on any upstream release
schedule.

```python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Ravengram!")


app.run()
```

**Ravengram** is a modern, elegant and asynchronous MTProto API framework. It enables you to easily interact
with the main Telegram API through a user account (custom client) or a bot identity (bot API alternative)
using Python.

### Key Features

- **Ready**: Install Ravengram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

This is currently a local, unpublished fork. Install it straight from your own clone:

``` bash
pip install -e .
```

Optional dependencies

``` bash
pip install -e ".[fast]"     # TgCrypto and uvloop for better performance
pip install -e ".[qrcode]"   # QR code login support
```

Once you push this to your own GitHub repo (see the `Source`/`Issues` URLs in `pyproject.toml`), replace
the command above with a `pip install git+https://github.com/ahmedahah4/ravengram` install, or publish it
to PyPI under your own package name.

### Website

The project site lives in `website/` (plain HTML/CSS/JS, no build step) and is published to GitHub Pages by
`.github/workflows/pages.yml` on every push to `master` that touches it. Preview it locally with
`python -m http.server -d website`.

### Keeping it up to date with Telegram's API

Telegram's raw API surface lives in the TL schema files under `compiler/api`, and the `pyrogram.raw` layer is
generated from them by the `compiler` package (see the `Makefile` for the `compile` target). When Telegram
ships new methods/types, update the schema there and re-run the compiler instead of waiting on an upstream
release.
