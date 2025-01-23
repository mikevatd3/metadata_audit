import re
import ast

import click


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


def camel_to_snake(name):
    """
    Convert a camelCase or PascalCase string to snake_case.
    """
    # Add an underscore before capital letters, then lowercase everything
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def get_classes_from_file(filepath):
    """Extract class names and their fields from a Python file."""
    with open(filepath, "r") as file:
        file_content = file.read()
    
    # Parse the file content into an AST
    tree = ast.parse(file_content, filename=filepath)
    
    class_metadata = {}
    
    # Iterate through the top-level nodes in the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Get the class name
            class_name = node.name
            
            # Collect all class-level fields (assignments)
            fields = [
                asgn.target.id for asgn in node.body
                if isinstance(asgn, ast.AnnAssign)
                and asgn.target.id != "Config"
            ]
            
            # Store metadata
            class_metadata[camel_to_snake(class_name)] = fields
    
    return class_metadata


@click.command()
@click.argument("filename")
def read_schema(filename):
    tables = get_classes_from_file(filename)
    
    result = []
    for table, variables in tables.items():
        if table == "config":
            continue

        result.append(TABLE_TEMPLATE.format(table_name=table))
        result.extend([
            VARIABLE_TEMPLATE.format(table_name=table, variable_name=var)
            for var in variables
        ])

        result.append(EDITION_TEMPLATE.format(table_name=table))
        result.append("\n")

    print("\n".join(result))


if __name__ == "__main__":
    read_schema()
