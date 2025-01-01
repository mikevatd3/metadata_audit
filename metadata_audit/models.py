from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship


Base = declarative_base() # Base class for all declarative models.


class Topic(Base):
    """
    Topic is the highest level of organization. It serves as a container
    for datasets that should live together in their own schema.
    """

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationship: one topic -> many tables
    tables: Mapped[List["Table"]] = relationship(back_populates="topic")


class Table(Base):
    """
    Table is the metadata for a database table. Each table can contain
    many editions of data.
    """

    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    unit_of_analysis: Mapped[Optional[str]] = mapped_column(String)
    universe: Mapped[Optional[str]] = mapped_column(String)
    owner: Mapped[Optional[str]] = mapped_column(String)
    collector: Mapped[Optional[str]] = mapped_column(String)
    collection_method: Mapped[Optional[str]] = mapped_column(String)
    collection_reason: Mapped[Optional[str]] = mapped_column(String)
    source_url: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    use_conditions: Mapped[Optional[str]] = mapped_column(Text)
    cadence: Mapped[Optional[str]] = mapped_column(String)

    # Foreign Key to Topic
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.id"))
    topic: Mapped[Topic] = relationship(back_populates="tables")

    # Relationships from Table -> Variables and Editions
    variables: Mapped[List["Variable"]] = relationship(back_populates="table")
    editions: Mapped[List["Edition"]] = relationship(back_populates="table")


class Variable(Base):
    """
    Variable is the metadata about a single column within a table.
    """

    __tablename__ = "variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_type: Mapped[Optional[str]] = mapped_column(
        String
    )  # e.g. "int64", "string", etc.
    parent_variable: Mapped[Optional[str]] = mapped_column(String)
    suppression_threshold: Mapped[Optional[float]] = mapped_column(Float)
    standard: Mapped[Optional[str]] = mapped_column(String)

    # Foreign Key linking each variable to one Table
    table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id"), nullable=False
    )
    table: Mapped[Table] = relationship(back_populates="variables")


class Edition(Base):
    """
    Most of our uploads are yearly or at most monthly. We break these out
    into 'editions' where we track when we added data to the system along
    with some other metadata notes.
    """

    __tablename__ = "editions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    num_records: Mapped[Optional[int]] = mapped_column(Integer)
    raw_path: Mapped[Optional[str]] = mapped_column(String)
    script_path: Mapped[Optional[str]] = mapped_column(String)
    version: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    published: Mapped[Optional[datetime]] = mapped_column(DateTime)
    acquired: Mapped[Optional[datetime]] = mapped_column(DateTime)
    updated: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Foreign Key linking each edition to one Table
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    table: Mapped[Table] = relationship(back_populates="editions")
