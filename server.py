import sys, os
sys.dont_write_bytecode = True

import json
import http.cookies as cookies

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from passlib.hash import bcrypt
import bcrypt as cryptb

from functions import *

gSessionStore = SessionStore()





class Handler(BaseHTTPRequestHandler):

	# >>>>>>>>>>>>>>>> CORS & CHECKING <<<<<<<<<<<<<<<<

	def end_headers(self):
		self.sendCookie()
		self.send_header("Access-Control-Allow-Origin", self.headers['Origin'])
		self.send_header("Access-Control-Allow-Headers", "Content-Type, Content-Length")
		self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		self.send_header("Access-Control-Allow-Credentials", "true")
		BaseHTTPRequestHandler.end_headers(self)

	def sendError(self, status_code, error):
		self.send_response(status_code)
		self.send_header("Content-Type", "text/plain")
		self.end_headers()
		self.wfile.write(error.encode("utf-8"))

	def checkPath(self, mask):
		mask_parts = mask[1:].split("/")
		path_parts = self.path[1:].rstrip("/").split("/")
		if len(mask_parts) != len(path_parts):
			self.url_vars = {}
			return False

		vars = {}
		for i in range(len(mask_parts)):
			if mask_parts[i][0] == "{":
				vars[mask_parts[i][1:-1]] = path_parts[i]
			else:
				if mask_parts[i] != path_parts[i]:
					self.url_vars = {}
					return False

		self.url_vars = vars
		return True

	def getJSON(self):
		if "Content-Length" not in self.headers:
			return (422, {})
		if self.headers["Content-Length"] == "0":
			return (422, {})

		raw_body = self.rfile.read(int(self.headers["Content-Length"]))

		try:
			body = json.loads(raw_body.decode("utf-8"))
		except json.decoder.JSONDecodeError:
			body = {}
			return (422, {})
		return (200, body)





	# >>>>>>>>>>>>>>>> COOKIES <<<<<<<<<<<<<<<<

	def loadCookie(self):
		if "Cookie" in self.headers:
			self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
		else:
			self.cookie = cookies.SimpleCookie()

	def sendCookie(self):
		if not hasattr(self, "cookie"):
			return

		for morsel in self.cookie.values():
			self.send_header("Set-Cookie", morsel.OutputString())





	# >>>>>>>>>>>>>>>> SESSIONS <<<<<<<<<<<<<<<<

	def loadSession(self):
		self.loadCookie()

		if not "sessionID" in self.cookie or not gSessionStore.contains(self.cookie["sessionID"].value):
			self.cookie["sessionID"] = gSessionStore.createSession()

		self.session = gSessionStore.getSession(self.cookie["sessionID"].value)





	# >>>>>>>>>>>>>>>> METHODS <<<<<<<<<<<<<<<<

	def do_OPTIONS(self):
		self.send_response(200)
		self.end_headers()

	def do_GET(self):
		self.loadSession()

		db = DB()

		# RETURN LOG INFORMATION FOR INQUIRED MONTH
		if self.checkPath("/logs/{month}"):
			logs = db.retrieveLogs(self.url_vars["month"])

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.wfile.write(json.dumps({
				"logs": logs
			}).encode("utf-8"))

		# RETURN LOG INFORMATION FOR TODAY (established by local time in functions.py)
		elif self.checkPath("/today"):
			if "UID" not in self.session:
				self.sendError(401, "Unauthorised Access.")
				return

			today = db.retrieveTodaysAmount()

			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

			self.wfile.write(json.dumps({
				"today": today
			}).encode("utf-8"))

		else:
			self.sendError(404, "Path Not Found.")

	def do_POST(self):
		self.loadSession()

		db = DB()

		# ADMIN LOGIN
		if self.checkPath("/authenticate"):
			status_code, body = self.getJSON()
			if status_code < 200 or status_code > 299:
				self.sendError(status_code, "Could not parse JSON from body.")
				return

			if "username" not in body or "encrypted_password" not in body:
				self.sendError(422, "Not all values in body.")
				return

			user = db.retrieveUser(body['username'])
			if not user:
				self.sendError(404, "User incorrect or not found.")
				return

			if not bcrypt.verify(body['encrypted_password'], user['encrypted_password']):
				self.sendError(401, "User incorrect or not found.")
				return

			self.session["UID"] = user["username"]

			self.send_response(201)
			self.send_header("Content-Type", "application/json")
			self.end_headers()

		# POST OR UPDATE TODAY (dependant on if information already logged)
		elif self.checkPath("/today"):
			if "UID" not in self.session:
				self.sendError(401, "Unauthorised Access")
				return

			status_code, body = self.getJSON()
			if status_code < 200 or status_code > 299:
				self.sendError(status_code, "Could not parse JSON from body.")
				return

			if "water" not in body:
				self.sendError(422, "Not all values in body.")
				return

			status_code, rtn = db.updateWater(body['water'])

			self.send_response(status_code)
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(rtn.encode("utf-8"))

		# CREATE ADMIN ACCOUNT
		# elif self.checkPath("/admin"):
		# 	length = int(self.headers["Content-Length"])
		# 	unparsed_body = self.rfile.read(length).decode("utf-8")

		# 	body = parse_qs(unparsed_body)

		# 	if "username" not in body or "encrypted_password" not in body:
		# 		self.sendError(422, "Missing required values")

		# 		return

		# 	body["encrypted_password"][0] = bcrypt.encrypt(body["encrypted_password"][0].encode("utf-8"))

		# 	status_code, rtn = db.insertUser(**body)
		# 	if status_code < 200 or status_code > 299:
		# 		self.sendError(status_code, rtn)

		# 		return

		# 	self.send_response(201)
		# 	self.send_header("Content-Type", "application/x-www-form-urlencoded")
		# 	self.end_headers()

		# 	self.wfile.write(bytes("Admin account created.", "utf-8"))
		
		else:
			self.sendError(404, "Path Not Found.")





# >>>>>>>>>>>>>>>> START RUNNING SERVER <<<<<<<<<<<<<<<<

def main():
	db = DB()
	db.createTables()
	db = None # disconnect

	port = 8080
	if len(sys.argv) > 1:
		port = int(sys.argv[1])

	listen = ("0.0.0.0", port)
	server = HTTPServer(listen, Handler)

	print("Listening...")
	server.serve_forever()

main()
