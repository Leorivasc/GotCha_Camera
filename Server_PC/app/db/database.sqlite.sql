BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cameras" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL UNIQUE,
	"ip_address"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL DEFAULT 8000,
	"path"	TEXT NOT NULL DEFAULT '/video_feed',
	"frameskip"	INTEGER DEFAULT 0,
	"detectionarea"	INTEGER DEFAULT 20,
	"detectionthreshold"	INTEGER NOT NULL DEFAULT 100,
	"recordtime"	INTEGER NOT NULL DEFAULT 20,
	"alertlength"	INTEGER NOT NULL DEFAULT 10,
	"isTriggerable"	INTEGER NOT NULL DEFAULT 1,
	"recordProcessed"	INTEGER NOT NULL DEFAULT 0,
	"isEnabled"	INTEGER NOT NULL DEFAULT 1,
	"mirrorport"	INTEGER NOT NULL DEFAULT 0 UNIQUE,
	"emailAlert"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "email" (
	"id"	INTEGER NOT NULL,
	"MAIL_SERVER"	TEXT NOT NULL DEFAULT 'smtp.gmail.com',
	"MAIL_PORT"	BLOB NOT NULL DEFAULT 465,
	"MAIL_USERNAME"	BLOB NOT NULL DEFAULT 'gmail_user',
	"MAIL_PASSWORD"	TEXT NOT NULL DEFAULT 'passwd',
	"MAIL_USE_TLS"	INTEGER NOT NULL DEFAULT 0,
	"MAIL_USE_SSL"	INTEGER NOT NULL DEFAULT 1,
	"MAIL_DEFAULT_SENDER"	TEXT NOT NULL DEFAULT 'sender@mail.com',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"username"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "cameras" ("id","name","ip_address","port","path","frameskip","detectionarea","detectionthreshold","recordtime","alertlength","isTriggerable","recordProcessed","isEnabled","mirrorport","emailAlert") VALUES (1,'localhost','127.0.0.1',8000,'/video_feed',1,1000,10,20,22,1,0,1,5001,'yourmail@email.com');
INSERT INTO "email" ("id","MAIL_SERVER","MAIL_PORT","MAIL_USERNAME","MAIL_PASSWORD","MAIL_USE_TLS","MAIL_USE_SSL","MAIL_DEFAULT_SENDER") VALUES (1,'your.smtp.server','465','mailuser','password',0,1,'from@mail.com');
INSERT INTO "users" ("id","username","password") VALUES (1,'admin','51b6a2b26c7d4b04e1891bfbf69f424d');
COMMIT;
