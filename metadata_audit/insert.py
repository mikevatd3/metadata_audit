from logging import Logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import metadata_audit.datatypes as typ
import metadata_audit.models as db
from metadata_audit.models import Base


def insert_metadata(
    topic: typ.Topic,
    table: typ.Table,
    variables: list[typ.Variable],
    edition: typ.Edition,
    session: Session,
    logger: Logger,
):
    logger.info("Creating all tables if not created.")
    Base.metadata.create_all(bind=session.get_bind())

    # 1) upsert topic
    topic_obj = (
        session.query(db.Topic)
        .filter(db.Topic.name == topic.name)
        .one_or_none()
    )
    if topic_obj:
        topic_obj.description = topic.description
    else:
        topic_obj = db.Topic(name=topic.name, description=topic.description)

    # 2) upsert table
    table_obj = (
        session.query(db.Table)
        .filter(db.Table.name == table.name)
        .one_or_none()
    )
    if table_obj:
        table_obj.description = table.description
        table_obj.unit_of_analysis = table.unit_of_analysis
        table_obj.universe = table.universe
        table_obj.owner = table.owner
        table_obj.collector = table.collector
        table_obj.collection_method = table.collection_method
        table_obj.collection_reason = table.collection_reason
        table_obj.source_url = table.source_url
        table_obj.notes = table.notes
        table_obj.use_conditions = table.use_conditions
        table_obj.cadence = table.cadence

    else:
        table_obj = db.Table(
            name=table.name,
            description=table.description,
            unit_of_analysis=table.unit_of_analysis,
            universe=table.universe,
            owner=table.owner,
            collector=table.collector,
            collection_method=table.collection_method,
            collection_reason=table.collection_reason,
            source_url=table.source_url,
            notes=table.notes,
            use_conditions=table.use_conditions,
            cadence=table.cadence,
        )

    topic_obj.tables.append(table_obj)

    # 3) upsert variables
    for var_data in variables:
        var_obj = (
            session.query(db.Variable)
            .filter(db.Variable.name == var_data.name)
            .filter(db.Variable.table_id == table_obj.id)
            .one_or_none()
        )
        if var_obj:
            var_obj.description = var_data.description
            var_obj.data_type = var_data.data_type
            var_obj.parent_variable = var_data.parent_variable
            var_obj.suppression_threshold = var_data.suppression_threshold
            var_obj.standard = var_data.standard
        else:
            var_obj = db.Variable(
                name=var_data.name,
                description=var_data.description,
                data_type=var_data.data_type,
                parent_variable=var_data.parent_variable,
                suppression_threshold=var_data.suppression_threshold,
                standard=var_data.standard,
            )

            table_obj.variables.append(var_obj)

    # 4) upsert edition
    edition_obj = (
        session.query(db.Edition)
        .filter(db.Edition.edition_date == edition.edition_date)
        .filter(db.Edition.table_id == table_obj.id)
        .one_or_none()
    )

    if edition_obj:
        edition_obj.num_records = edition.num_records
        edition_obj.raw_path = edition.raw_path
        edition_obj.script_path = edition.script_path
        edition_obj.notes = edition.notes
        edition_obj.start = edition.start
        edition_obj.end = edition.end
        edition_obj.published = edition.published
        edition_obj.acquired = edition.acquired

    else:
        edition_obj = db.Edition(
            edition_date=edition.edition_date,
            num_records=edition.num_records,
            raw_path=edition.raw_path,
            script_path=edition.script_path,
            version=edition.version,
            notes=edition.notes,
            start=edition.start,
            end=edition.end,
            published=edition.published,
            acquired=edition.acquired,
        )

        table_obj.editions.append(edition_obj)

    try:
        session.add(topic_obj)  # This cascades all children
        session.commit()

        logger.info("Metadata successfully inserted/updated!")

    except SQLAlchemyError as e:
        session.rollback()
        logger.error("Error during insertion:", e)
        logger.error("No metadata added.")

    finally:
        session.close()
