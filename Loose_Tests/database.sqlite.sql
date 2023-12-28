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
	"mirrorport"	INTEGER NOT NULL UNIQUE,
	"isTriggerable"	INTEGER NOT NULL DEFAULT 1,
	"isEnabled"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "cameras" ("id","name","ip_address","port","path","frameskip","detectionarea","recordtime","mirrorport","isTriggerable","isEnabled") VALUES (1,'PiZero1','192.168.137.45',8000,'/video_feed',2,400,20,5001,1,1),
 (2,'Pi2','192.168.137.151',8000,'/video_feed',2,400,20,5002,1,1),
 (3,'LaptopLeo','127.0.0.1',8000,'/video_feed',2,400,20,5003,0,1);
COMMIT;
