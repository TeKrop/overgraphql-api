"""The schema is the API documentation: every type, field and argument
exposed by the API must carry a description.
"""

import pytest

from app.graphql.schema import schema

BUILTIN_SCALARS = {"String", "Int", "Float", "Boolean", "ID"}

INTROSPECTION_QUERY = """
{
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        description
        args { name description }
      }
      enumValues { name }
    }
  }
}
"""


@pytest.fixture(scope="module")
def schema_types() -> list[dict]:
    result = schema.execute_sync(INTROSPECTION_QUERY)

    assert result.errors is None
    assert result.data is not None
    return [
        schema_type
        for schema_type in result.data["__schema"]["types"]
        if not schema_type["name"].startswith("__")
        and schema_type["name"] not in BUILTIN_SCALARS
    ]


def test_every_type_has_a_description(schema_types):
    undocumented = [
        schema_type["name"]
        for schema_type in schema_types
        if not schema_type["description"]
    ]

    assert undocumented == []


def test_every_field_has_a_description(schema_types):
    undocumented = [
        f"{schema_type['name']}.{field['name']}"
        for schema_type in schema_types
        for field in schema_type["fields"] or []
        if not field["description"]
    ]

    assert undocumented == []


def test_every_argument_has_a_description(schema_types):
    undocumented = [
        f"{schema_type['name']}.{field['name']}({arg['name']}:)"
        for schema_type in schema_types
        for field in schema_type["fields"] or []
        for arg in field["args"]
        if not arg["description"]
    ]

    assert undocumented == []
