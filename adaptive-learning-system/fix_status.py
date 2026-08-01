import sqlite3
db = sqlite3.connect('data/app.db')
db.execute("UPDATE learning_sessions SET status = 'active' WHERE status = 'ACTIVE';")
db.execute("UPDATE learning_sessions SET status = 'completed' WHERE status = 'COMPLETED';")
db.execute("UPDATE learning_sessions SET status = 'needs_remediation' WHERE status = 'NEEDS_REMEDIATION';")
db.execute("UPDATE learning_sessions SET status = 'stopped' WHERE status = 'STOPPED';")
db.commit()
print("Fixed statuses!")
