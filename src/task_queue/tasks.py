from celery import Celery, Task
from celery.utils.log import get_task_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import PROJECT_SETTINGS
from model.email import NotificationType, SystemEmail

from .config import Config

logger = get_task_logger(__name__)


app = Celery("tasks")
app.config_from_object(Config)


# Celery doesn't work with async:
engine = create_engine(
    str(PROJECT_SETTINGS.SQLALCHEMY_DATABASE_URL_SYNC),
)
SessionMaker = sessionmaker(
    bind=engine,
)


@app.task(
    bind=True,
    ignore_result=True,  # you don't need the results here
    track_started=True,
    rate_limit="60/m",  # per worker instance rate limit
    max_retries=3,
    retry_backoff=3 * 60,  # exponential backoff
    compression="gzip",
)
def send_email(self: Task, product_id: int) -> str:
    """Send the email with a task, and save the email (with status) + task ID
    in the database. After the task is complete, update the email status to
    "sent". This should be handled by a SystemEmail SQLAlchemy model.

    Args:
        self (Task): task, see
        https://docs.celeryq.dev/en/stable/userguide/tasks.html#task-request
        session (AsyncSession): the session object
        product_id (int): target product's primary key

    Raises:
        self.retry: Retry if failed. See:
        https://docs.celeryq.dev/en/stable/reference/celery.app.task.html#celery.app.task.Task.retry
    """
    try:
        task_id = str(self.request.id)
        logger.debug(
            f"Executing task {task_id}: Sending product creation email..."
        )

        session = SessionMaker()

        # save system email (status: not sent)
        system_email = SystemEmail(
            task_id=task_id,
            target_id=product_id,
            type=NotificationType.PRODUCT,
        )
        session.add(system_email)
        session.commit()

        # TODO send email, query for product info

        # update system email status
        system_email.is_sent = True
        session.commit()

        return system_email.task_id
    except Exception as exc:
        logger.debug(
            f"An exception occurred while sending email for task#{task_id}!"
        )
        raise self.retry(exc=exc)
    finally:
        session.close()
