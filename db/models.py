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
    name: str = SQL.Column(SQL.Text, nullable=False)
    spotify_user_id: str = SQL.Column(SQL.Text, nullable=False)
    spotify_access_token: str = SQL.Column(SQL.Text, nullable=False)
    started_by_fpjs_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    started_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)
    paused_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)
    ended_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)


class QueueSubscribers(BaseModel):
    """Table of subscribers to Mixify queue."""

    __tablename__ = 'queue_subscribers'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id: str = SQL.Column(UUID(as_uuid=True), SQL.ForeignKey(Queues.id), nullable=False)
    spotify_access_token: str = SQL.Column(SQL.Text, nullable=False)
    fpjs_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    subscribed_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)

    __table_args__ = (
        SQL.UniqueConstraint('queue_id', 'spotify_access_token'),
    )

    queue: Queues = SQL.relationship('Queues')


class QueueSongs(BaseModel):
    """Table of songs in Mixify queues."""

    __tablename__ = 'queue_songs'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id: str = SQL.Column(UUID(as_uuid=True), SQL.ForeignKey(Queues.id), nullable=False)
    name: str = SQL.Column(SQL.Text, nullable=False)
    artist: str = SQL.Column(SQL.Text, nullable=False)
    album_cover_url: str = SQL.Column(SQL.Text, nullable=False)
    duration_ms: int = SQL.Column(SQL.Integer, nullable=False)
    spotify_track_id: str = SQL.Column(SQL.Text, nullable=False)
    spotify_track_uri: str = SQL.Column(SQL.Text, nullable=False)
    added_by_fpjs_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    added_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)
    added_to_spotify_queue_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)
    played_on_utc: datetime.datetime | None = SQL.Column(SQL.DateTime)

    queue: Queues = SQL.relationship('Queues')


class QueueSongUpvotes(BaseModel):
    """Table of upvotes on songs in Mixify queues."""

    __tablename__ = 'queue_song_upvotes'

    id: uuid.UUID = SQL.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_song_id: str = SQL.Column(
        UUID(as_uuid=True), SQL.ForeignKey(QueueSongs.id), nullable=False)
    upvoted_by_fpjs_visitor_id: str = SQL.Column(SQL.Text, nullable=False)
    upvoted_on_utc: datetime.datetime = SQL.Column(SQL.DateTime, nullable=False)

    __table_args__ = (
        SQL.UniqueConstraint('queue_song_id', 'upvoted_by_fpjs_visitor_id'),
    )

    queue_song: QueueSongs = SQL.relationship('QueueSongs')
