"""MongoDB access. One MongoClient per process, created on first use."""
from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient


@lru_cache(maxsize=1)
def get_client():
    return MongoClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
    )


def get_database():
    return get_client()[settings.MONGODB_DB]


def get_students_collection():
    return get_database()["students"]
