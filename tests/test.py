import asyncio
import functools
from datetime import datetime, timedelta
from functools import lru_cache, wraps


def timed_lru_cache(seconds: int = 20, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        async def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            print("Something is happening before the function is called.")
            return await func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache

# def foo():
#     def wrapper(func):
#         @functools.wraps(func)
#         async def wrapped(*args):
#              # Some fancy foo stuff
#             return await func(*args)
#         return wrapped
#     return wrapper

# async def my_decorator(func):
#     async def wrapper(*args, **kwargs):
#         print("Something is happening before the function is called.")
#         await func(*args, **kwargs)
#         print("Something is happening after the function is called.")
#         # return f
#     return await wrapper()


@timed_lru_cache()
async def say_whee():
    print("Whee!")


# say_whee = my_decorator(say_whee)
newfeature = asyncio.get_event_loop().run_until_complete(say_whee())
# say_whee()
# asyncio.run()
# 1st decorator - to call coroutine
# 2nd decorator - to cache result
