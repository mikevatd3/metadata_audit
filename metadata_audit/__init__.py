from pathlib import Path
import json
import logging
import logging.config
from sqlalchemy import create_engine
import tomli


# Walk out the the module base path
with open(Path().cwd() / "config.toml", "rb") as f:
    config = tomli.load(f)


db_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
)


def setup_logging():
    with open(Path.cwd() / "logging_config.json") as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)


TABLE_TEMPLATE = """
[tables.{table_name}]
name="{table_name}"
description = ""
unit_of_analysis = ""
universe = ""
owner = ""
collector = ""
# collection_method = "Leave commented if not using"
collection_reason = ""
source_url = ""
# notes = "Leave commented if not using"
# use_conditions = "Leave commented if not using"
# cadence = "Leave commented if not using"
"""

VARIABLE_TEMPLATE = """
[[tables.{table_name}.variables]]
name = "{variable_name}"
description = ""
parent_variable = ""
# suppression_threshold = "Leave commented if not using."
# standard = "Leave commented if not using."
"""

EDITION_TEMPLATE = """
[tables.{table_name}.editions.<edition date>]
edition_date = "<edition date>"
notes = "First upload of this dataset"
raw_path = ""
start = "<start date>" 
end = "9999-12-31" # Forever
published = "<published date>"
acquired = "<acquired date>" 
"""

