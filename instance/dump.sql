PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('5616e9d1660e');
CREATE TABLE clubs_and_societies (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	image_path VARCHAR(255), 
	created_at DATETIME, 
	CONSTRAINT pk_clubs_and_societies PRIMARY KEY (id)
);
INSERT INTO clubs_and_societies VALUES(1,'Science Club','Innovators and scientists','scienceclub.jpg','2025-10-20 14:57:54.065718');
CREATE TABLE systems (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	created_at DATETIME, 
	CONSTRAINT pk_systems PRIMARY KEY (id)
);
INSERT INTO systems VALUES(1,'844','2025-10-15 08:26:31.589001');
INSERT INTO systems VALUES(2,'CBC','2025-10-15 09:17:21.554961');
INSERT INTO systems VALUES(3,'IGCSE','2025-10-19 09:16:34.573115');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	created_at DATETIME, 
	role VARCHAR(120) NOT NULL, 
	CONSTRAINT pk_users PRIMARY KEY (id), 
	CONSTRAINT uq_users_email UNIQUE (email)
);
INSERT INTO users VALUES(1,'admin',X'2432622431322459435441666b55583374553134336d724b64776a377548547768366f6878795749735354434665585779675073355855322f762e71','admin@gmail.com','2025-10-14 11:45:49.765089','Admin');
INSERT INTO users VALUES(3,'user',X'24326224313224424d6248787a49342f524e6c4975734c6731782f304f39615a786d69644834317658375854434a664f62486f30793044316e476f75','user@gmail.com','2025-10-15 07:54:15.423842','User');
CREATE TABLE departments (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	created_at DATETIME, 
	system_id INTEGER NOT NULL, 
	CONSTRAINT pk_departments PRIMARY KEY (id), 
	CONSTRAINT fk_departments_system_id_systems FOREIGN KEY(system_id) REFERENCES systems (id)
);
INSERT INTO departments VALUES(1,'Sciences','2025-10-15 08:27:38.615774',1);
INSERT INTO departments VALUES(2,'Humanities','2025-10-15 09:17:08.051097',1);
INSERT INTO departments VALUES(4,'Social Sciences','2025-10-15 10:52:07.120388',2);
INSERT INTO departments VALUES(6,'Technical','2025-10-16 07:06:39.036729',1);
INSERT INTO departments VALUES(7,'STEM','2025-10-16 18:26:42.083327',2);
INSERT INTO departments VALUES(8,'Arts','2025-10-19 09:16:52.220210',2);
CREATE TABLE tracks (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	department_id INTEGER NOT NULL, 
	CONSTRAINT pk_tracks PRIMARY KEY (id), 
	CONSTRAINT fk_tracks_department_id_departments FOREIGN KEY(department_id) REFERENCES departments (id)
);
INSERT INTO tracks VALUES(5,'Pure Science',7);
INSERT INTO tracks VALUES(6,'PE',8);
CREATE TABLE subjects (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	track_id INTEGER, 
	system_id INTEGER, 
	department_id INTEGER NOT NULL, 
	CONSTRAINT pk_subjects PRIMARY KEY (id), 
	CONSTRAINT fk_subjects_department_id_departments FOREIGN KEY(department_id) REFERENCES departments (id), 
	CONSTRAINT fk_subjects_system_id_systems FOREIGN KEY(system_id) REFERENCES systems (id), 
	CONSTRAINT fk_subjects_track_id_tracks FOREIGN KEY(track_id) REFERENCES tracks (id)
);
INSERT INTO subjects VALUES(1,'Physics',NULL,1,1);
INSERT INTO subjects VALUES(4,'Biology(CBC)',5,2,7);
INSERT INTO subjects VALUES(5,'Chemistry',NULL,1,1);
INSERT INTO subjects VALUES(6,'Geography',NULL,1,2);
INSERT INTO subjects VALUES(7,'IRE',NULL,1,2);
INSERT INTO subjects VALUES(8,'IRE',NULL,2,4);
INSERT INTO subjects VALUES(9,'Physics',5,2,7);
CREATE TABLE fee_structures (
	id INTEGER NOT NULL, 
	file_path VARCHAR(255) NOT NULL, 
	updated_at DATETIME, 
	CONSTRAINT pk_fee_structures PRIMARY KEY (id)
);
INSERT INTO fee_structures VALUES(1,'uploads/fee_structures/fee_structure.pdf','2025-10-16 08:03:08.783751');
CREATE TABLE about_us_images (
	id INTEGER NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	filepath VARCHAR(255) NOT NULL, 
	uploaded_at DATETIME, 
	updated_at DATETIME, 
	CONSTRAINT pk_about_us_images PRIMARY KEY (id)
);
INSERT INTO about_us_images VALUES(1,'f4bb96f78b3b4eb79c40d2cde7a4a2a6_staffroom2.jpg','About_images/f4bb96f78b3b4eb79c40d2cde7a4a2a6_staffroom2.jpg','2025-10-21 07:57:52.393401','2025-10-21 07:57:52.393405');
CREATE TABLE alumnis (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	current_title VARCHAR(200), 
	year_of_completion VARCHAR(10), 
	comment VARCHAR(500) NOT NULL, 
	image_path VARCHAR(200), 
	CONSTRAINT pk_alumnis PRIMARY KEY (id)
);
INSERT INTO alumnis VALUES(2,'Leo','Teacher','1567','It was an amazing experience, ghitheri was good.','Screenshot_2025-02-10_083726.png');
INSERT INTO alumnis VALUES(3,'Alex Brown','Business man','2004','Amazing School','20251009_OHR.WebbPillars_EN-US0251661895_UHD_bing.jpg');
CREATE TABLE subject_selections (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	subjects TEXT NOT NULL, 
	created_at DATETIME, 
	system_id INTEGER NOT NULL, 
	department_id INTEGER NOT NULL, 
	track_id INTEGER, 
	CONSTRAINT pk_subject_selections PRIMARY KEY (id), 
	CONSTRAINT fk_subject_selections_department_id_departments FOREIGN KEY(department_id) REFERENCES departments (id), 
	CONSTRAINT fk_subject_selections_system_id_systems FOREIGN KEY(system_id) REFERENCES systems (id), 
	CONSTRAINT fk_subject_selections_track_id_tracks FOREIGN KEY(track_id) REFERENCES tracks (id)
);
INSERT INTO subject_selections VALUES(1,'Selection A','["Physics", "Chemistry", "Biology"]','2025-10-18 15:05:43.899066',1,1,'');
INSERT INTO subject_selections VALUES(2,'GeoIRE','["Geography", "IRE", "History"]','2025-10-19 09:22:35.078395',1,2,'');
INSERT INTO subject_selections VALUES(3,'Sel B','["Biology", "Physics"]','2025-10-22 08:35:41.248350',1,1,NULL);
COMMIT;
