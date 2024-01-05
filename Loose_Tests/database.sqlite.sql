BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cameras" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL UNIQUE,
	"ip_address"	TEXT NOT NULL,
	"port"	INTEGER NOT NULL DEFAULT 8000,
	"path"	TEXT NOT NULL DEFAULT '/video_feed',
	"frameskip"	INTEGER DEFAULT 0,
	"detectionarea"	INTEGER DEFAULT 20,
	"recordtime"	INTEGER NOT NULL DEFAULT 20,
	"alertlength"	INTEGER NOT NULL DEFAULT 10,
	"isTriggerable"	INTEGER NOT NULL DEFAULT 1,
	"isEnabled"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "cameras" ("id","name","ip_address","port","path","frameskip","detectionarea","recordtime","alertlength","isTriggerable","isEnabled") VALUES (1,'PiZero1','192.168.1.14',8000,'/video_feed',4,300,20,5,1,1),
 (2,'Pi2','192.168.1.12',8000,'/video_feed',4,300,20,10,1,1),
 (3,'LaptopLeo','192.168.1.17',8000,'/video_feed',2,300,20,10,0,0);
COMMIT;
