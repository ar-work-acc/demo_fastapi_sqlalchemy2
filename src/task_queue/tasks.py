"""
Note: Celery doesn't provide explicit asyncio support. You might want to find
a better service to use.
(RuntimeError: asyncio.run() cannot be called from a running event loop)

Normally, you would want to use tasks to run CPU intensive jobs, not IO-bound
ones. This is just for demo purposes, not actually the best way to deal with
it.
"""

from celery import Celery, Task
from celery.utils.log import get_task_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import repository.email as repo_email
from core.config import PROJECT_SETTINGS
from model.email import NotificationType, SystemEmail

from .config import Config

# Celery doesn't work with async, so we need to use a synchronous session
engine = create_engine(
    str(PROJECT_SETTINGS.SQLALCHEMY_DATABASE_URL_SYNC),
)
SessionMaker = sessionmaker(
    bind=engine,
)

logger = get_task_logger(__name__)

# Celery app
celery_app = Celery("tasks")
celery_app.config_from_object(Config)


def create_and_send_system_email(
    session: Session,
    task_id: str,
    product_id: int,
) -> SystemEmail:
    """Create system email for the product, send it, and update its status.

    Args:
        session (Session): The synchronous session object.
        task_id (str): Celery task UUID.
        product_id (int): PK of target product.

    Returns:
        SystemEmail: The system email object created.
    """
    repo_email.create_system_email(
        session,
        task_id=task_id,
        target_id=product_id,
        type=NotificationType.PRODUCT,
    )
    # TODO send email, query for current product info to construct it
    system_email = repo_email.update_system_email_status(
        session, task_id, status=True
    )
    return system_email


@celery_app.task(
    bind=True,
    queue="default",
    ignore_result=True,  # you don't need the results here
    track_started=True,
    rate_limit="60/m",  # per worker instance rate limit
    max_retries=3,
    retry_backoff=3 * 60,  # exponential backoff
    compression="gzip",
)
def send_email(self: Task, product_id: int) -> str:
    """
    Task to send a system notification email for product creation.

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
            f"Executing task #{task_id}: Sending product creation email..."
        )
        session = SessionMaker()
        system_email = create_and_send_system_email(
            session, task_id, product_id
        )

        return system_email.task_id
    except Exception as exc:
        logger.debug(
            f"An exception occurred while sending email for task#{task_id}!"
        )
        raise self.retry(exc=exc)
    finally:
        session.close()
