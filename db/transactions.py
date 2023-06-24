"""PostgreSQL database transation module."""
import typing

import errors
from db import connection


def save_entry(entry: object, commit: bool) -> typing.Any:
    """Saves an entry to the database.

    :param entry: database entry instance
    :param commit: commits immediately if True
    :returns: saved entry
    """
    connection.SQL.session.add(entry)  # pylint: disable=no-member
    if commit:
        _commit_transaction()
    return entry


def delete_entry(entry: object, commit: bool) -> typing.Any:
    """Deletes an entry from the database.

    :param entry: database entry instance
    :param commit: commits immediately if True
    :returns: deleted entry
    """
    connection.SQL.session.delete(entry)  # pylint: disable=no-member
    if commit:
        _commit_transaction()
    return entry


def update_properties() -> None:
    """Update entry properties in the database."""
    _commit_transaction()


def _commit_transaction() -> None:
    """Commits a database transaction.

    :raises errors.DatabaseError: if unable to commit transaction
    """
    try:
        connection.SQL.session.commit()  # pylint: disable=no-member
    except Exception as error:
        raise errors.DatabaseError(f'{str(error)}')
