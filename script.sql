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

-- Turputevka определение (ИСПРАВЛЕНО: Страна теперь TEXT)
CREATE TABLE Turputevka (
    "Код путевки" INTEGER,
    Страна TEXT, -- Было INTEGER, стало TEXT
    "Дата первого дня" TEXT,
    Продолжительность INTEGER,
    Транспорт TEXT,
    Питание TEXT,
    Программа TEXT,
    Цена REAL,
    Фото TEXT,
    CONSTRAINT Turputevka_PK PRIMARY KEY ("Код путевки")
);

-- Zakaz определение (ИСПРАВЛЕНО: добавлен PK, изменен тип даты)
CREATE TABLE Zakaz (
    "Код заказа" INTEGER,
    "Код путевки" INTEGER,
    "Код клиента" INTEGER,
    Количество INTEGER,
    "Дата заказа" TEXT, -- Было INTEGER, стало TEXT
    Скидка INTEGER,
    CONSTRAINT Zakaz_PK PRIMARY KEY ("Код заказа"), -- Добавлен первичный ключ
    CONSTRAINT Zakaz_Klients_FK FOREIGN KEY ("Код клиента") REFERENCES Klients("Код клиента") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Zakaz_Turputevka_FK FOREIGN KEY ("Код путевки") REFERENCES Turputevka("Код путевки") ON DELETE CASCADE ON UPDATE CASCADE
);