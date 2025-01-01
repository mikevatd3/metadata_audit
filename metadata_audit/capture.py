from pathlib import Path
from .datatypes import Topic, Table, Edition
from .git import log_git
from .insert import insert_metadata

def record_metadata(
    schema, 
    file, 
    table_name, 
    metadata, 
    edition_date, 
    cleaned,
    session,
    logger,
    lax=False,
):
    logger.info("Reached record_metadata function.")
    schema_dict = schema.to_json_schema()
    schema_variables = schema_dict["properties"]

    for variable in metadata["tables"][table_name]["variables"]:
        variable["data_type"] = schema_variables[variable["name"]]["items"][
            "type"
        ]

    # Validate base topic -- it skips the recursive check
    topic = Topic(**metadata)

    # Pydantic Validation of current Table metadata
    table = Table(**metadata["tables"][table_name])

    # Pydantic Validation of Edition metadata

    edition_dict = metadata["tables"][table_name]["editions"][edition_date]
    script_path = Path(file).resolve()

    edition_dict["version"] = log_git(script_path, lax=lax)
    edition_dict["script_path"] = str(script_path)
    edition_dict["num_records"] = len(cleaned)

    edition = Edition(**edition_dict)
    
    insert_metadata(
        topic,
        table,
        table.variables,
        edition,
        session,
        logger,
    )
