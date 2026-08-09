from app.worker.celery_app import celery
from app.services.indexing_service import IndexingService
from app.core.redis import redis_client
import json

indexing_service = IndexingService()


@celery.task(bind=True)
def index_repository_task(self, repository_path: str):

    task_id = self.request.id

    print("\n" + "=" * 80)
    print("CELERY TASK ID:", task_id)
    print("=" * 80)

    redis_client.hset(
        task_id,
        mapping={
            "status": "STARTED",
            "stage": "Queued",
            "progress": 0,
        },
    )

    print("REDIS AFTER FIRST HSET")
    print(redis_client.hgetall(task_id))

    try:

        result = indexing_service.index_repository(
            repository_path=repository_path,
            task_id=task_id,
        )

        redis_client.set(
            f"profile:{task_id}",
            json.dumps(result["repository_profile"])
        )

        redis_client.hset(
            task_id,
            mapping={
                "status": "SUCCESS",
                "stage": "Repository Indexed",
                "progress": 100,
            },
        )

        print("REDIS AFTER SUCCESS")
        print(redis_client.hgetall(task_id))

        return result

    except Exception as e:

        redis_client.hset(
            task_id,
            mapping={
                "status": "FAILED",
                "stage": "Indexing Failed",
                "error": str(e),
            },
        )

        print("REDIS AFTER FAILURE")
        print(redis_client.hgetall(task_id))

        raise