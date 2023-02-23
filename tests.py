
import main


def test_get_data():
    json_data = main.get_wufoo_data()

    assert len(json_data) >= 10


def test_table_created():
    connection, cursor = main.open_db("wufoo_data.db")
    main.create_entries_table(cursor)
    cursor.execute("SELECT Count() FROM SQLITE_MASTER WHERE name = ?", ["entries"])
    record = cursor.fetchone()
    number_of_rows = record[0]  # the number is the first )and only) item in the tuple
    assert number_of_rows == 1
