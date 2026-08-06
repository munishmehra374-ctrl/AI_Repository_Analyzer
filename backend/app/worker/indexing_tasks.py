from app.worker.celery_app import celery
from app.services.indexing_service import IndexingService
from app.core.redis import redis_client

indexing_service = IndexingService()


@celery.task(bind=True)
def index_repository_task(self, repository_path: str):

    task_id = self.request.id

    # Initial Status
    redis_client.hset(
        task_id,
        mapping={
            "status": "STARTED",
            "stage": "Queued",
            "progress": 0,
        },
    )

    try:

        result = indexing_service.index_repository(
            repository_path,
            task_id,
        )

        redis_client.hset(
            task_id,
            mapping={
                "status": "SUCCESS",
                "stage": "Repository Indexed",
                "progress": 100,
            },
        )

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

        raise