import os
import leveldb

from plenum.common.exceptions import StorageException
from plenum.common.log import getlogger

logger = getlogger()


class VerkeyStore:
    guardianPrefix = b'\xf0\x9f\x98\x80'

    def __init__(self, basedir: str, name='verkey_store'):
        logger.debug('Initializing verkey {} store at {}'.format(name, basedir))
        self._basedir = basedir
        self._name = name
        self._db = None
        self.open()

    def get(self, did, unpack=False):
        self._checkDb()
        value = self._db.Get(did)
        if unpack and value.startsWith(self.guardianPrefixDecoded):
            return self.get(value[len(self.guardianPrefixDecoded):])
        return value

    def set(self, did, value, guarded=False):
        self._checkDb()
        if guarded:
            value = self.guardianPrefixDecoded + value
        self._db.Put(did, value)

    def close(self):
        self._db = None

    def open(self):
        self._db = leveldb.LevelDB(self.dbName())

    def dbName(self):
        return os.path.join(self._basedir, self._name)

    def _checkDb(self):
        if not self._db:
            raise StorageException('Db reference is missing!')

    @property
    def guardianPrefixDecoded(self):
        return bytes.decode(VerkeyStore.guardianPrefix)