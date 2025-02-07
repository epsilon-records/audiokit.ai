from celery import Celery

# Configure Celery with Redis as broker and backend
celery_app = Celery("audiokit_ai", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def process_audio_task(task_name: str, audio_file_path: str):
    # Dummy background task for processing audio
    return f"Processed {task_name} for file {audio_file_path}" 