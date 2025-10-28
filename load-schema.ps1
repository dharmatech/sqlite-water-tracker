
# sqlite3 .\sqlite-water-tracker.db < .\schema.sql

Get-Content .\schema.sql | sqlite3.exe .\sqlite-water-tracker.db