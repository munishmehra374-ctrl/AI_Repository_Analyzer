from app.core.redis import redis_client

task_id = "5e5cfb75-2cdb-4d06-a14a-76c2c8366ad7"

print(redis_client.hgetall(task_id))