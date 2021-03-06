# WATER LOGGER
Logging my personal water intake for me to edit and for you to see.


## Endpoints
#### GET
* `/logs/{month}` - Returns JSON object "logs" with a list of objects that describe the DID (date ID) and "amount" of water in oz.
* `/today` - Requires authorised admin login. Simply retrieves the amount of water that has been logged today (date is dynamically determined in `functions.py`).

#### POST
* `/authenticate` - Checks admin login verification of username and password. A session UID is initialised and enables login until cookie is cleared from browser.
* `/today` - Requires authorised admin login.  If some amount of water is already logged for the day, the 
* `/admin` - Should be depricated after first time use. Creates the admin account for access to authorised permissions.

## Schema
I've organised the data by month, so that the client only needs to `GET` the information up through the current month.  Therefore, 12 'month' tables are created, and one admin table.  This can be done via the server at runtime.  For the sake of convenience, I will show just one month's example, plus the admin table.
```
CREATE TABLE IF NOT EXISTS admin (
	UID SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE,
	encrypted_password VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS january (
	DID INTEGER PRIMARY KEY,
	amount INTEGER
);
```

## To Do
- [x] &nbsp; Counter to see how many days I've had over 50 fl oz of water (since 183 days is my goal)
- [x] &nbsp; Sleeping dyno loading gif thing
- [x] &nbsp; Use MST instead of GMT for updating
	* **edit: NOT A JAVASCRIPT/PYTHON ISSUE!**
	* `heroku config:add TZ="America/Denver"`
- [ ] &nbsp; Fix to POST new entries (CORS issue?).  Temporary fix is to manually insert 0 values into monthly tables, but it's very inconvenient.  Only added 0s up through February.
- [ ] &nbsp; Enable to log entires on mobile.  Also fix to stay logged in after authentication.
- [ ] &nbsp; Fill up the boxes depending on progress to 50 fl oz?  Might look too busy.
