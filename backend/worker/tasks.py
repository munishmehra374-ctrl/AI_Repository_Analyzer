from app.worker.celery_app import celery


@celery.task
def test_task():
    return "Celery is working!"