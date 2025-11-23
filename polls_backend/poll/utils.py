# poll/utils.py
import redis
from django.conf import settings
from rest_framework.exceptions import Throttled

# Connect to Redis (matches docker-compose host)
redis_client = redis.Redis(host='redis', port=6379, db=0)

def rate_limit(user_id: int, action: str, limit: int, window_seconds: int):
    """
    Generic Redis rate-limiter.
    
    user_id:        current user ID
    action:         'vote', 'create_poll', etc.
    limit:          how many times allowed
    window_seconds: sliding window (ex: 30 sec, 60 sec)
    """
    key = f"rl:{action}:{user_id}"

    # Increase count
    current_count = redis_client.incr(key)

    # Set expiry if first time
    if current_count == 1:
        redis_client.expire(key, window_seconds)

    # If exceeding limit
    if current_count > limit:
        raise Throttled(detail=f"Rate limit exceeded. Try again later.")
