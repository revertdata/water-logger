import sys, os, base64
sys.dont_write_bytecode = True

import psycopg2
import psycopg2.extras
import urllib.parse

import random
import string

import datetime
import time


def dict_factory(cursor, row):
	d = {}
	for i, col in enumerate(cursor.description):
		d[col[0]] = row[i]
	return d





# >>>>>>>>>>>>>>>> SESSIONS <<<<<<<<<<<<<<<<

class SessionStore:
	def __init__(self):
		self.sessionStore = {}
		
		return

	def createSession(self):
		rnum = os.urandom(32)
		ID = base64.b64encode(rnum).decode("utf-8")
		self.sessionStore[ID] = {}
		
		return ID

	def getSession(self, ID):
		if ID in self.sessionStore:
			return self.sessionStore[ID]
			
		return None

	def delSession(self,ID):
		if ID in self.sessionStore:
			del self.sessionStore[ID]

		return self.getSession[ID]

	def contains(self, key):
		return key in self.sessionStore





# >>>>>>>>>>>>>>>> DATABASE <<<<<<<<<<<<<<<<

class DB:

	# ---------------- CON/DE/STRUCTORS ----------------

	def __init__(self):
		urllib.parse.uses_netloc.append("postgres")
		url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

		self.connection = psycopg2.connect(
			cursor_factory=psycopg2.extras.RealDictCursor,
			database=url.path[1:],
			user=url.username,
			password=url.password,
			host=url.hostname,
			port=url.port
		)

		self.cursor = self.connection.cursor()

	def __del__(self):
		self.connection.close()

	def createTables(self):
		self.cursor.execute("CREATE TABLE IF NOT EXISTS admin (UID SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE, encrypted_password VARCHAR(255))")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS january (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS february (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS march (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS april (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS may (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS june (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS july (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS august (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS september (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS october (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS november (DID INTEGER PRIMARY KEY, amount INTEGER)")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS december (DID INTEGER PRIMARY KEY, amount INTEGER)")

		self.connection.commit()



	# ---------------- INSERT ----------------

	def insertUser(self, **args):
		if "username" not in args or "encrypted_password" not in args:
			return (400, "Missing arguments.")

		username = args["username"][0].lower()

		self.cursor.execute("INSERT INTO admin (username, encrypted_password) VALUES (%s, %s)", (username, args["encrypted_password"][0]))
		self.connection.commit()

		return (201, "User created.")



	# ---------------- RETRIEVE ----------------

	def retrieveLogs(self, month):
		self.cursor.execute("SELECT * FROM {}".format(month))

		return self.cursor.fetchall()

	def retrieveTodaysAmount(self):
		now = datetime.datetime.now()
		month = time.strftime("%B")

		self.cursor.execute(("SELECT * FROM {} WHERE did = %s").format(month), (now.day, ))

		return self.cursor.fetchone()

	def retrieveUser(self, username):
		self.cursor.execute("SELECT * FROM admin WHERE username = %s", (username, ))
		
		return self.cursor.fetchone()



	# ---------------- UPDATE OR CREATE ----------------

	def updateWater(self, water):
		now = datetime.datetime.now()
		month = time.strftime("%B")

		if self.retrieveTodaysAmount() == 0:
			self.cursor.execute("INSERT INTO {} (did, amount) VALUES (%s, %s)".format(month), (now.day, water))
			self.connection.commit()

			return (201, "Water log created.")

		else:
			self.cursor.execute("SELECT amount FROM {} WHERE did = %s".format(month), (now.day, ))
			rows = self.cursor.fetchall()

			for row in rows:
				amount = row['amount']
				tot = "{}".format(int(water)+int(amount))

			self.cursor.execute("UPDATE {} SET amount = %s WHERE did = %s".format(month), (tot, now.day))
			self.connection.commit()
			
			return (200, "Water amount updated.")
