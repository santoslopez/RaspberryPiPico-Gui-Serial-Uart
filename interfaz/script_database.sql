/*
Archivo de base de datos para SQLite (No para SQL)
Se coloco la extension del archivo ".sql" para que el editor de texto
reconozca la sintaxis SQL

Pero este fue pensado para corre en SQLite

*/
CREATE TABLE "usuarios" (
	"idUsuario"	INTEGER NOT NULL,
	"usuario"	TEXT NOT NULL,
	"password"	TEXT,
	PRIMARY KEY("idUsuario" AUTOINCREMENT)
);

CREATE TABLE vecinos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombreGrupo TEXT NOT NULL
)

CREATE TABLE "mensajes" (
	"id"	INTEGER NOT NULL,
	"tipoMensaje"	TEXT NOT NULL,
	"mensaje"	TEXT,
	"fecha"	TEXT,
	idUsuario INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("idUsuario") REFERENCES "usuarios"("idUsuario")
)