import sqlite3
DATABASE_PATH = 'database/test.db'

def register(chat_id,reg_number,pwd):
	conn = sqlite3.connect(DATABASE_PATH)
	conn.execute("INSERT INTO UserInformation (ChatId,RegistrationNumber,Password) VALUES (?,?,?)",(chat_id,reg_number,pwd))
	conn.commit()
	conn.close()

def is_registered(chat_id):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("SELECT * FROM UserInformation where ChatId = ?",(chat_id,))
	row = cur.fetchone()
	conn.close()
	if (row is not None):
		return row[1]
	return False

def unregister(chat_id):
	conn = sqlite3.connect(DATABASE_PATH)
	try:
		print chat_id
		cur = conn.execute("DELETE FROM UserInformation where ChatId = ?",(chat_id,))
		conn.commit()
	except:
		conn.close()
		return false;
	conn.close()
	return True;

def set_timetable(chat_id,timetable_message,hash):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("Update UserInformation Set TimeTableHash = ? WHERE ChatId = ?",(hash,chat_id))
	curr = conn.execute("SELECT * FROM TimeTable WHERE TimeTableHash = ?",(hash,))
	row = curr.fetchone()
	if row is None:
		curr = conn.execute("INSERT INTO TimeTable (TimeTableHash,TimeTableMessage) VALUES (?,?)",(hash,timetable_message))
	conn.commit()
	conn.close()

def get_register_number(chat_id):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("SELECT RegistrationNumber FROM UserInformation WHERE ChatId = ?",(chat_id,))
	row = cur.fetchone()
	conn.close()
	return row[0]


def get_credentials(chat_id):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("SELECT RegistrationNumber,Password FROM UserInformation WHERE ChatId = ?",(chat_id,))
	row = cur.fetchone()
	conn.close()
	return row[0],row[1]

def get_timetable(chat_id):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("SELECT TimeTableHash FROM UserInformation WHERE ChatId = ?",(chat_id,))
	row = cur.fetchone()
	if row[0] is None:
		conn.close()
		return False
	timetable_message = get_timetable_message(row[0])
	if timetable_message is '':
		conn.close()
		return False
	conn.close()
	return timetable_message

def get_timetable_message(hash):
	conn = sqlite3.connect(DATABASE_PATH)
	cur = conn.execute("Select TimeTableMessage FROM TimeTable WHERE TimeTableHash = ?",(hash,))
	row = cur.fetchone()
	conn.close()
	return row[0]
