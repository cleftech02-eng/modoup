from sqlalchemy.orm import configure_mappers

from database import Base
import model


def test_all_models_are_registered():
    expected_tables = {
        "users",
        "realms",
        "lessons",
        "lesson_completions",
        "activities",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables)


def test_models_have_primary_keys():
    for table in Base.metadata.tables.values():
        assert len(list(table.primary_key.columns)) > 0


def test_foreign_keys_are_defined():
    assert Base.metadata.tables["lessons"].c.realm_id.foreign_keys
    assert Base.metadata.tables["lesson_completions"].c.user_id.foreign_keys
    assert Base.metadata.tables["lesson_completions"].c.lesson_id.foreign_keys
    assert Base.metadata.tables["activities"].c.user_id.foreign_keys


def test_lesson_completion_unique_constraint():
    table = Base.metadata.tables["lesson_completions"]
    names = {constraint.name for constraint in table.constraints}
    assert "unique_user_lesson" in names


def test_sqlalchemy_relationships_configure():
    configure_mappers()
