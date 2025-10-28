import sqlite3
import argparse

def main():
    parser = argparse.ArgumentParser(description='Load a schema into a SQLite database.')
    parser.add_argument('db_file', help='The SQLite database file.')
    args = parser.parse_args()

    try:
        with open('schema.sql', 'r') as f:
            schema = f.read()

        conn = sqlite3.connect(args.db_file)
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        print(f"Successfully loaded schema from schema.sql into {args.db_file}")

    except FileNotFoundError:
        print("Error: schema.sql not found in the current directory.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
