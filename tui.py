import sys
import os
import sqlite3

DB_FILE = "sqlite-water-tracker.db"
DEFAULT_OUNCES = 8.0

def get_char():
    # Cross-platform single character input
    try:
        # Windows
        import msvcrt
        return msvcrt.getch().decode()
    except ImportError:
        # Unix-like
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def show_water_log():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- Full Water Log ---")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, ounces FROM water_log ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\nNo entries found in the water log.")
        else:
            print("\n{:<25} {:<10}".format("Timestamp", "Ounces"))
            print("-" * 35)
            for row in rows:
                print("{:<25} {:<10.2f}".format(row[0], row[1]))

    except sqlite3.OperationalError:
        print(f"\nError: Could not find the 'water_log' table in '{DB_FILE}'.")
        print("Please ensure the database schema has been loaded.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    input("\nPress Enter to return to the menu.")

def show_daily_summary():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- Daily Summary ---")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT date, total, weight, target, percent_of_target FROM water_log_full ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\nNo summary data found.")
        else:
            print("\n{:<12} {:<10} {:<10} {:<10} {:<20}".format("Date", "Total (oz)", "Weight", "Target", "% of Target"))
            print("-" * 62)
            for row in rows:
                # Handle None values for weight, target, and percent_of_target
                weight = f"{row[2]:.2f}" if row[2] is not None else "N/A"
                target = f"{row[3]:.2f}" if row[3] is not None else "N/A"
                percent = f"{row[4]:.2f}" if row[4] is not None else "N/A"
                print("{:<12} {:<10.2f} {:<10} {:<10} {:<20}".format(row[0], row[1], weight, target, percent))

    except sqlite3.OperationalError:
        print(f"\nError: Could not find the 'water_log_full' view in '{DB_FILE}'.")
        print("Please ensure the database schema has been loaded.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    input("\nPress Enter to return to the menu.")

def drink_water():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO water_log (timestamp, ounces) VALUES (datetime('now', 'localtime'), ?)", (DEFAULT_OUNCES,))
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Error: Could not write to 'water_log' table in '{DB_FILE}'.")
        print("Please ensure the database schema has been loaded.")
        input("\nPress Enter to return to the menu.")
    except Exception as e:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"An unexpected error occurred: {e}")
        input("\nPress Enter to return to the menu.")

def set_default_ounces():
    global DEFAULT_OUNCES
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- Set Default Ounces ---")
    try:
        new_ounces_str = input(f"Enter new default ounces (current: {DEFAULT_OUNCES}): ")
        new_ounces = float(new_ounces_str)
        if new_ounces > 0:
            DEFAULT_OUNCES = new_ounces
        else:
            print("Please enter a positive number.")
            input("\nPress Enter to continue.")
    except ValueError:
        print("Invalid input. Please enter a number.")
        input("\nPress Enter to continue.")

def remove_last_entry():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- Remove Most Recent Entry ---")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Using id is safer for identifying the row to delete
        cursor.execute("SELECT id, timestamp, ounces FROM water_log ORDER BY id DESC LIMIT 1")
        last_entry = cursor.fetchone()

        if not last_entry:
            print("\nNo entries to remove.")
            conn.close()
        else:
            print("\nThis is the most recent entry:")
            print(f"  Timestamp: {last_entry[1]}")
            print(f"  Ounces:    {last_entry[2]}")

            confirm = input("\nAre you sure you want to remove this entry? (y/n): ").lower()

            if confirm == 'y':
                cursor.execute("DELETE FROM water_log WHERE id = ?", (last_entry[0],))
                conn.commit()
                print("\nEntry removed.")
            else:
                print("\nRemoval cancelled.")
        
        conn.close()

    except sqlite3.OperationalError:
        print(f"\nError: Could not access the 'water_log' table in '{DB_FILE}'.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    input("\nPress Enter to return to the menu.")

def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- Water Tracker TUI ---")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Fetch last 10 entries
        cursor.execute("SELECT timestamp, ounces FROM water_log ORDER BY timestamp DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        print("\n--- Last 10 Entries ---")
        if not rows:
            print("No entries found.")
        else:
            print("{:<25} {:<10}".format("Timestamp", "Ounces"))
            print("-" * 35)
            for row in reversed(rows): # reverse to show oldest of the 10 first
                print("{:<25} {:<10.2f}".format(row[0], row[1]))

    except sqlite3.OperationalError:
        print("\nCould not display recent entries. 'water_log' table not found.")
    except Exception as e:
        print(f"\nAn error occurred while fetching recent entries: {e}")

    print("\n\n--- Menu ---")
    print(f"[d] Drink water ({DEFAULT_OUNCES} oz)")
    print("[s] Set default ounces")
    print("[r] Remove most recent entry")
    print("[1] Show full water log")
    print("[2] Show daily summary")
    print("[q] Quit")
    print("-------------------------")

def main():
    while True:
        main_menu()
        choice = get_char()

        if choice.lower() == 'd':
            drink_water()
        elif choice.lower() == 's':
            set_default_ounces()
        elif choice.lower() == 'r':
            remove_last_entry()
        elif choice == '1':
            show_water_log()
        elif choice == '2':
            show_daily_summary()
        elif choice.lower() == 'q':
            os.system('cls' if os.name == 'nt' else 'clear')
            break

if __name__ == "__main__":
    main()
