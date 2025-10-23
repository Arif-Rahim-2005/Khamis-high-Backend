# import sqlite3
# import psycopg2

# # Path to your SQLite DB file
# sqlite_db_path = "school.db"  # <-- change this to your actual SQLite file

# # Connect to SQLite
# sqlite_conn = sqlite3.connect(sqlite_db_path)
# sqlite_cur = sqlite_conn.cursor()

# # Connect to Neon Postgres
# pg_conn = psycopg2.connect(
#     "postgresql://neondb_owner:npg_KAflHrdX25ao@ep-raspy-salad-ag6zgnpz-pooler.c-2.eu-central-1.aws.neon.tech/Khamisdb?sslmode=require&channel_binding=require"
# )
# pg_cur = pg_conn.cursor()

# # Get all table names from SQLite
# sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = [t[0] for t in sqlite_cur.fetchall()]

# for table in tables:
#     print(f"Migrating table: {table}")

#     # Get columns
#     sqlite_cur.execute(f"PRAGMA table_info({table});")
#     columns = [c[1] for c in sqlite_cur.fetchall()]
#     col_str = ", ".join(columns)

#     # Fetch all rows
#     sqlite_cur.execute(f"SELECT * FROM {table};")
#     rows = sqlite_cur.fetchall()

#     for row in rows:
#         placeholders = ", ".join(["%s"] * len(row))
#         # Convert any bytes to string to preserve bcrypt hashes correctly
#         clean_row = [str(x) if isinstance(x, bytes) else x for x in row]
#         try:
#             pg_cur.execute(
#                 f'INSERT INTO {table} ({col_str}) VALUES ({placeholders})',
#                 clean_row
#             )
#         except Exception as e:
#             print(f"Error inserting into {table}: {e}")


# pg_conn.commit()
# pg_cur.close()
# pg_conn.close()
# sqlite_cur.close()
# sqlite_conn.close()

# print("Migration complete!")
import sqlite3
import psycopg2
from datetime import datetime

# Path to your SQLite DB file
sqlite_db_path = "school.db"  # <-- change this to your actual SQLite file

# Connect to SQLite
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cur = sqlite_conn.cursor()

# Connect to Neon Postgres
pg_conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_KAflHrdX25ao@ep-raspy-salad-ag6zgnpz-pooler.c-2.eu-central-1.aws.neon.tech/Khamisdb?sslmode=require&channel_binding=require"
)
pg_cur = pg_conn.cursor()

# Get all table names from SQLite
sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in sqlite_cur.fetchall()]

for table in tables:
    print(f"Migrating table: {table}")

    # Get columns
    sqlite_cur.execute(f"PRAGMA table_info({table});")
    columns_info = sqlite_cur.fetchall()
    columns = [c[1] for c in columns_info]
    col_str = ", ".join(columns)

    # Fetch all rows
    sqlite_cur.execute(f"SELECT * FROM {table};")
    rows = sqlite_cur.fetchall()

    for row in rows:
        placeholders = ", ".join(["%s"] * len(row))
        clean_row = []

        for idx, value in enumerate(row):
            # Convert bytes to string
            if isinstance(value, bytes):
                clean_row.append(value.decode('utf-8'))
            # Convert SQLite DATETIME string to Python datetime for Postgres
            elif columns_info[idx][2].upper() in ("DATETIME", "TIMESTAMP") and isinstance(value, str):
                try:
                    clean_row.append(datetime.fromisoformat(value))
                except ValueError:
                    clean_row.append(value)  # leave as-is if parsing fails
            else:
                clean_row.append(value)

        try:
            pg_cur.execute(
                f'INSERT INTO {table} ({col_str}) VALUES ({placeholders})',
                clean_row
            )
        except Exception as e:
            print(f"Error inserting into {table}: {e}")

pg_conn.commit()
pg_cur.close()
pg_conn.close()
sqlite_cur.close()
sqlite_conn.close()

print("Migration complete!")
