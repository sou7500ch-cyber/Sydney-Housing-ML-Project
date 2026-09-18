from database import (
    create_property,
    get_all_properties,
    get_property,
    update_property,
    delete_property,
)


def test_create_property():
    property_id = create_property(
        "Blacktown",
        170,
        2026,
        9,
        "R2"
    )

    assert property_id > 0

    delete_property(property_id)


def test_get_property():
    property_id = create_property(
        "Chatswood",
        250,
        2026,
        8,
        "R1"
    )

    property_record = get_property(property_id)

    assert property_record is not None
    assert property_record[0] == property_id
    assert property_record[1] == "Chatswood"
    assert property_record[2] == 250.0
    assert property_record[3] == 2026
    assert property_record[4] == 8
    assert property_record[5] == "R1"

    delete_property(property_id)


def test_get_all_properties():
    property_id = create_property(
        "Parramatta",
        200,
        2026,
        7,
        "R2"
    )

    properties = get_all_properties()

    property_ids = [property_record[0] for property_record in properties]

    assert property_id in property_ids

    delete_property(property_id)


def test_update_property():
    property_id = create_property(
        "Blacktown",
        150,
        2026,
        6,
        "R2"
    )

    rows_updated = update_property(
        property_id,
        "Parramatta",
        220,
        2026,
        10,
        "R1"
    )

    assert rows_updated == 1

    updated_record = get_property(property_id)

    assert updated_record is not None
    assert updated_record[1] == "Parramatta"
    assert updated_record[2] == 220.0
    assert updated_record[3] == 2026
    assert updated_record[4] == 10
    assert updated_record[5] == "R1"

    delete_property(property_id)


def test_delete_property():
    property_id = create_property(
        "Chatswood",
        180,
        2026,
        5,
        "C4"
    )

    rows_deleted = delete_property(property_id)

    assert rows_deleted == 1
    assert get_property(property_id) is None


def test_get_nonexistent_property():
    property_record = get_property(999999)

    assert property_record is None