-- Klients определение

CREATE TABLE Klients (
	"Код клиента" INTEGER,
	Фамилия TEXT,
	Имя TEXT,
	Отчество TEXT,
	Город TEXT,
	Адрес TEXT,
	CONSTRAINT Klients_PK PRIMARY KEY ("Код клиента")
);


-- Users определение

CREATE TABLE Users (
	id INTEGER,
	login TEXT,
	parol TEXT,
	"role" TEXT,
	CONSTRAINT Users_PK PRIMARY KEY (id)
);


-- Turputevka определение

CREATE TABLE Turputevka (
	"Код путевки" INTEGER,
	Страна INTEGER,
	"Дата первого дня" TEXT,
	Продолжительность INTEGER,
	Транспорт TEXT,
	Питание TEXT,
	Программа TEXT,
	Цена REAL,
	Фото TEXT,
	CONSTRAINT Turputevka_PK PRIMARY KEY ("Код путевки")
);


-- Zakaz определение

CREATE TABLE Zakaz (
	"Код заказа" INTEGER,
	"Код путевки" INTEGER,
	"Код клиента" INTEGER,
	Количество INTEGER,
	"Дата заказа" INTEGER,
	Скидка INTEGER,
	CONSTRAINT Zakaz_Klients_FK FOREIGN KEY ("Код клиента") REFERENCES Klients("Код клиента") ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT Zakaz_Turputevka_FK FOREIGN KEY ("Код путевки") REFERENCES Turputevka("Код путевки") ON DELETE CASCADE ON UPDATE CASCADE
);