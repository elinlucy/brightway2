# -*- coding: utf-8 -*
import os
from . import config
from time import time
import json
try:
    import cPickle as pickle
except ImportError:
    import pickle


class SerializedDict(object):
    """Base class for dictionary that can be serlialized to of unserialized from disk. Uses JSON as its storage format. Has most of the methods of a dictionary.

    Upon instantiation, the serialized dictionary is read from disk."""
    def __init__(self):
        if not getattr(self, "_filename"):
            raise NotImplemented("SerializedDict must be subclassed, and the filename must be set.")
        self._filepath = os.path.join(config.dir, self._filename)
        self.load()

    def load(self):
        """Load the serialized data. Creates the file if not yet present."""
        try:
            self.data = self.deserialize()
        except IOError:
            # Create if not present
            self.data = {}
            self.flush()

    def flush(self):
        """Serialize the current data to disk."""
        self.serialize()

    @property
    def list(self):
        """List the keys of the dictionary. This is a property, and does not need to be called."""
        return sorted(self.data.keys())

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.flush()

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        return self.__unicode__()

    def __delitem__(self, name):
        del self.data[name]
        self.flush()

    def iteritems(self):
        return self.data.iteritems()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def serialize(self, filepath=None):
        """Method to do the actual serialization. Can be replaced with other serialization formats.

        Args:
            *filepath* (str, optional): Provide an alternate filepath (e.g. for backup).

        """
        with open(filepath or self._filepath, "w") as f:
            json.dump(self.pack(self.data), f, indent=2)

    def deserialize(self):
        """Load the serialized data. Can be replaced with other serialization formats."""
        return self.unpack(json.load(open(self._filepath, "r")))

    def pack(self, data):
        """Transform the data, if necessary. Needed because JSON must have strings as dictionary keys."""
        return data

    def unpack(self, data):
        """Return serialized data to true form."""
        return data

    def backup(self):
        """Write a backup version of the data to the ``backups`` directory."""
        filepath = os.path.join(config.dir, "backups",
            self._filename + ".%s.backup" % int(time()))
        self.serialize(filepath)


class PickledDict(SerializedDict):
    """Subclass of ``SerializedDict`` that uses the pickle format instead of JSON."""
    def serialize(self):
        with open(self._filepath, "wb") as f:
            pickle.dump(self.pack(self.data), f,
                protocol=pickle.HIGHEST_PROTOCOL)

    def deserialize(self):
        return self.unpack(pickle.load(open(self._filepath, "rb")))
