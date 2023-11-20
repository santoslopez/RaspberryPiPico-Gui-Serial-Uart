/*
Archivo de base de datos para SQLite (No para SQL)
Se coloco la extension del archivo ".sql" para que el editor de texto
reconozca la sintaxis SQL

Pero este fue pensado para corre en SQLite

*/
CREATE TABLE vecinos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombreGrupo TEXT NOT NULL
)

CREATE TABLE "mensajes" (
	"id"	INTEGER NOT NULL,
	"tipoMensaje"	TEXT NOT NULL,
	"mensaje"	TEXT,
	"fecha"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)