# db/redis.py
# import redis.asyncio as aioredis

# redis_client = None

# async def init_redis():
#     global redis_client
#     redis_client = aioredis.Redis(
#         host="localhost",
#         port=6379,
#         db=0,
#         decode_responses=True
#     )