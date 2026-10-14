import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ntgcalls import NTgCalls

from .chat_lock import ChatLock
from .methods import Methods
from .mtproto import MtProtoClient
from .scaffold import Scaffold
from .statictypes import statictypes
from .types import Cache


class PyTgCalls(Methods, Scaffold):
    WORKERS = min(32, (os.cpu_count() or 0) + 4)
    CACHE_DURATION = 60 * 60

    @statictypes
    def __init__(
        self,
        app: Any,
        workers: int = WORKERS,
        cache_duration: int = CACHE_DURATION,
    ):
        super().__init__()
        self._mtproto = app
        self._app = MtProtoClient(
            cache_duration,
            self._mtproto,
        )
        self._is_running = False
        self._cache_user_peer = Cache()
        self._binding = NTgCalls()
        # Bound for real in `start()`: the client may run on a loop that does not exist
        #  yet, so the one current at construction time is not necessarily the right one.
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = None
        self.workers = workers
        self._chat_lock = ChatLock()
        self.executor = ThreadPoolExecutor(
            self.workers,
            thread_name_prefix='Handler',
        )

    @property
    def cache_user_peer(self) -> Cache:
        return self._cache_user_peer

    @property
    def mtproto_client(self):
        return self._mtproto
