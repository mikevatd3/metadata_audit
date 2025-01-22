# metadata_capture

A tool for storing metadata using Pandera and Postgres.

You can use the `convert_schema` command to convert a file with defined Pandera schemas into toml format.

A file like this:

```
# schema.py

import pandera as pa


class TableSchema(pa.DataFrameModel):
    field_one: int = pa.Field()
    field_two: str = pa.Field()

```

```bash
(env) blah/blah> convet_schema path/to/schema.py
```

And the following will print (use `>>` to append it to your metadata.toml):

```
[tables.table_schema]
description = ""
unit_of_analysis = ""
universe = ""
owner = ""
collector = ""
# collection_method = ""
collection_reason = ""
source_url = ""
# notes = "Leave commented if not using"
# use_conditions = "Leave commented if not using"
# cadence = "Leave commented if not using"


[[tables.skills.variables]]
name = "field_one"
description = ""

[[tables.skills.variables]]
name = "field_two"
description = ""
```
