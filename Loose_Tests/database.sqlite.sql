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
	"mirrorport"	INTEGER NOT NULL DEFAULT 0 UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "cameras" ("id","name","ip_address","port","path","frameskip","detectionarea","recordtime","alertlength","isTriggerable","isEnabled","mirrorport") VALUES (1,'PiZero1','192.168.137.91',8000,'/video_feed',4,1000,20,10,1,1,5000),
 (2,'Pi2','192.168.137.151',8000,'/video_feed',4,1000,20,10,1,1,5001),
 (3,'LaptopLeo','192.168.137.1',8000,'/video_feed',2,300,20,10,0,0,5002),
 (4,'Localhost','127.0.0.1',8000,'/video_feed',4,1600,10,10,0,0,5003),
 (5,'Vst','134.171.190.34',80,'/mjpg/video.mjpg',0,800,20,10,0,0,5004);
COMMIT;
