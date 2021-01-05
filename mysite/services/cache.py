import redis
from decouple import config

r = redis.StrictRedis(host=config('REDIS_HOST'), port=config('REDIS_PORT'))


class Cache:

    @staticmethod
    def set_cache(key, value):
        """
        takes key[id] and value[token] value as inputs and stores it in redis server and has expiration time of 60 seconds
        """
        r.set(key, value)
        r.expire(key, time=8000)

    @staticmethod
    def get_cache(key):
        """
        it takes key as input and returns value stored with that key
        """
        return r.get(key)

    @staticmethod
    def delete_cache(key):
        """

        :param key: [mandatory]:key of cache record to be deleted
        """
        r.delete(key)






#factory for cache