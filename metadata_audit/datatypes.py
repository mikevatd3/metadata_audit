from typing import Any
from pydantic import BaseModel
from datetime import datetime


class Topic(BaseModel):
    """
    Topic is the highest level of organization. It serves as a container
    for datasets that should live together in their own schema.
    """

    name: str
    description: str
    tables: dict[str, Any] # avoiding the recursive check


class Table(BaseModel):
    """
    Table is the metadata for a database table. Each table can contain
    many editions of data.
    """
    # Required fields
    name: str
    description: str
    unit_of_analysis: str
    variables: list['Variable']
    editions: dict[str, Any] # again, avoiding the recursive check
    
    # Optional fields, set to None by default
    universe: str | None = None
    owner: str | None = None
    collector: str | None = None
    collection_method: str | None = None
    collection_reason: str | None = None
    source_url: str | None = None
    notes: str | None = None
    use_conditions: str | None = None
    cadence: str | None = None


class Variable(BaseModel):
    # Required fields
    name: str
    description: str
    data_type: str # This is provided by pandas / pandera
    
    # Optional fields
    parent_variable: str | None = None
    suppression_threshold: float | None = None # Float is more generaic
    standard: str | None = None  # This is for common defined standards
    # Future: max, min, mean, mode, entropy


class Edition(BaseModel):
    """
    Most of our uploads are yearly or at most monthly. We break these out
    into 'editions' where we track when we added data to the system along
    with some other metadata notes.
    """
    edition_date: datetime  # provided by script
    num_records: int  # provided by pandas
    raw_path: str # Path to the raw file
    script_path: str # Provided out of the script
    version: str # Provided from pygit
    published: datetime
    acquired: datetime
    
    # Start and end are special -- still trying to figure out how to deal
    notes: str | None = None
    start: datetime | None = None
    end: datetime | None = None


