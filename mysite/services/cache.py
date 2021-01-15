import redis
from decouple import config


class Cache:
    """
    Instantiates cache object and returns same instance for further operations using getInstance()
    """

    __shared_instance = None

    @staticmethod
    def getInstance():
        """[returns initialised cache instance to calling view]
        :return: cache instance stored in __shared_instance
        """

        if Cache.__shared_instance == None:
            Cache(config('REDIS_HOST'),config('REDIS_PORT'))
        return Cache.__shared_instance

    def __init__(self,host,port):
        """[initializes a cache instance with host and port]

        :param host: host to be set for redis
        :param port: port number to be set for redis
        """

        Cache.__shared_instance = redis.StrictRedis(host=host,port=port)


















