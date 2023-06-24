"""Module containing Mixify database models."""
import datetime
import typing
import uuid

from sqlalchemy.dialects.postgresql import UUID

from db import transactions
from db.connection import SQL

# Do not display these columns in request responses
HIDE_COLUMNS = ['password', 'account_token']


class BaseModel(SQL.Model):  # type: ignore
    """Base class for all Mixify database models."""

    __abstract__ = True

    def save(self, commit: bool = True) -> typing.Any:
        """Save entry to database.

        :param commit: immediately commit operation to DB, defaults to True
        :returns: saved entry
        """
        return transactions.save_entry(self, commit)

    def delete(self, commit: bool = True) -> typing.Any:
        """Delete entry from database.

        :param commit: immediately commit operation to DB, defaults to True
        :returns: deleted entry
        """
        return transactions.delete_entry(self, commit)

    def update(self) -> None:
        """Update entry properties."""
        transactions.update_properties()

    def as_dict(self) -> dict[str, typing.Any]:
        """Returns JSON serializable representation of entry."""
        return {column.key: getattr(self, column.key, None)
                for column in self.__table__.columns
                if column.key not in HIDE_COLUMNS}


class Queues(BaseModel):
    """Table of Mixify queues."""

    __tablename__ = 'queues'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: str = SQL.Column(SQL.Text, nullable=False)
    access_token: str = SQL.Column(SQL.Text, nullable=False)
    started_by_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    started_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)
    ended_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)


class QueueTracks(BaseModel):
    """Table of tracks in Mixify queues."""

    __tablename__ = 'queue_tracks'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id: str = SQL.Column(UUID(as_uuid=True), SQL.ForeignKey(Queues.id), nullable=False)
    track_id: str = SQL.Column(SQL.Text, nullable=False)
    track_name: str = SQL.Column(SQL.Text, nullable=False)
    track_artist: str = SQL.Column(SQL.Text, nullable=False)
    track_album_cover_url: str = SQL.Column(SQL.Text, nullable=False)
    track_length: str = SQL.Column(SQL.Text, nullable=False)
    added_by_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    added_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)
    played_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)

    queue: Queues = SQL.relationship('Queues')


class QueueTrackUpvotes(BaseModel):
    """Table of upvotes on tracks in Mixify queues."""

    __tablename__ = 'queue_track_upvotes'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_track_id: str = SQL.Column(
        UUID(as_uuid=True), SQL.ForeignKey(QueueTracks.id), nullable=False)
    upvoted_by_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    upvoted_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)

    __table_args__ = (
        SQL.UniqueConstraint('queue_track_id', 'upvoted_by_visitor_id'),
    )

    queue_track: QueueTracks = SQL.relationship('QueueTracks')
