#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

"""`pyrogram.calls` is part of the package, reached from a client as `app.calls`.

The calls engine loads a native library, so it stays out of `import pyrogram` and is only
built the first time a client asks for it.
"""

from __future__ import annotations as _annotations

import pkgutil
import subprocess
import sys
from importlib import import_module

import pyrogram.calls
from pyrogram import Client
from pyrogram.calls import PyTgCalls


def _client() -> Client:
    return Client("calls", api_id=1, api_hash="0" * 32, in_memory=True)


def test_import_pyrogram_does_not_load_the_calls_engine() -> None:
    probe = "import sys, pyrogram; print('ntgcalls' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "False"


def test_every_calls_module_imports() -> None:
    prefix = pyrogram.calls.__name__ + "."

    for module in pkgutil.walk_packages(pyrogram.calls.__path__, prefix):
        import_module(module.name)


def test_a_client_has_one_calls_instance_bound_to_itself() -> None:
    app = _client()

    calls = app.calls

    assert isinstance(calls, PyTgCalls)
    assert app.calls is calls
    assert calls.mtproto_client is app


def test_two_clients_do_not_share_their_calls() -> None:
    assert _client().calls is not _client().calls


def test_the_calls_bridge_takes_a_ravengram_client_as_pyrogram() -> None:
    assert _client().calls._app.package_name == "pyrogram"
