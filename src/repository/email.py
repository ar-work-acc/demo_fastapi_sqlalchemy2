"""
Note that this repository uses "synchronous" operations (for use in Celery tasks).
"""

from sqlalchemy.orm import Session

from model.email import NotificationType, SystemEmail


def create_system_email(
    session: Session,
    task_id: str,
    target_id: int,
    type: NotificationType,
) -> SystemEmail:
    """Create a system email (status = not sent)

    Args:
        session (Session): The session object.
        task_id (str): Celery task UUID.
        target_id (int): The primary key of the target object.
        type (NotificationType): Type of object to be notified of its creation.
    """
    system_email = SystemEmail(
        task_id=task_id,
        target_id=target_id,
        type=type,
    )
    session.add(system_email)
    session.commit()

    return system_email


def update_system_email_status(
    session: Session,
    system_email_task_id: str,
    status: bool = True,
) -> SystemEmail:
    """Update the `is_sent` status of a system email.

    Args:
        session (Session): The session object.
        system_email_task_id (str): The PK, or task UUID, of the system email.
        status (bool, optional): The new `is_sent` status. Defaults to True.
    """
    system_email = session.get(SystemEmail, system_email_task_id)
    if system_email is None:
        raise ValueError(f"System email not found: {system_email_task_id}")

    system_email.is_sent = status
    session.commit()

    return system_email
