import os
import sqlite3
import sys


def print_schema(db_path: str) -> None:
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        sys.exit(1)

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    )
    table_names = [row[0] for row in cursor.fetchall()]

    for table_name in table_names:
        safe_table_name = table_name.replace("'", "''")
        print(f"TABLE: {table_name}")
        print("cid|name|type|notnull|default|pk")

        cursor.execute(f"PRAGMA table_info('{safe_table_name}')")
        for cid, col_name, col_type, notnull, default, pk in cursor.fetchall():
            print(f"{cid}|{col_name}|{col_type}|{notnull}|{default}|{pk}")

        print("")

        cursor.execute(f"PRAGMA foreign_key_list('{safe_table_name}')")
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print("foreign_keys: id|seq|table|from|to|on_update|on_delete|match")
            for fk in foreign_keys:
                fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
                print(
                    f"foreign_keys: {fk_id}|{seq}|{ref_table}|{from_col}|{to_col}|{on_update}|{on_delete}|{match}"
                )
            print("")

    connection.close()


if __name__ == "__main__":
    db_file_path = os.path.join("Rsafety", "db.sqlite3")
    print_schema(db_file_path)



