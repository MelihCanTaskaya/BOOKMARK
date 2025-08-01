Installation and Run:

1
Windows: 	python -m venv venv
venv\Scripts\activate

Linux/Mac:	python3 -m venv venv
source venv/bin/activate	

2
	In terminal
		cd to ..\BOOKMARK \Bookmark Manager Backend
	and
		pip install -r requirements.txt

3
	Open run.py
	And run

4
	At this point backend is working.

5
	📁Go to Bookmark Frontend folder  register.html


Structure For frontend
•	login.html – User login page
•	register.html – User registration page
•	index.html – Bookmark dashboard
•	script.js – All frontend logic (API communication, rendering, etc.)
•	styles.css – Basic styling for layout and UI

Instructions
1.	Open register.html in your browser to create a new user account.
2.	After registering, use login.html to authenticate.
3.	Once logged in, you will be redirected to index.html, where you can:
o	Add bookmarks
o	View and filter bookmarks by tag
o	View most visited bookmarks
o	Assign or remove tags from bookmarks
o	Edit or delete existing entries

Design Decisions
•	Backend: Flask (Python) + SQLAlchemy for ORM
•	Authentication: JWT-based stateless authentication
•	Frontend: Vanilla JS + HTML/CSS for minimal setup and fast loading
•	Database: SQLite by default, but easily extendable (e.g., PostgreSQL)
•	Security: CORS configured to allow frontend communication only from localhost:5173 (adjustable)

