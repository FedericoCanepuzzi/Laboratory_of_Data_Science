import pyodbc
import csv

def insert(conn, reader, table):

    #eseguo una query per ottenere le colonne della tabella table da INFORMATION_SCHEMA.COLUMNS
    cursorc = conn.cursor()
    sql = ('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME= \''+table+'\'')
    cursorc.execute(sql)
    col = []
    for row in cursorc:
        col.append(row[0])
    cursorc.close()

    #eseguo la query per inserire le righe nel database
    cursor = conn.cursor()
    i=0
    for row in reader:
        i=i+1
        #utilizzo il parametro table, le col trovate e un array di len(col) punti interrogativi in values
        sql = ('INSERT INTO ' + table + ' (' + ','.join(col) + ') VALUES ('+','.join(['?']*len(col))+')')
        val = []
        for c in col:
            if row[c]!='':
                val.append(row[c])
            else:
                val.append(None)
        #eseguo la query parametrica con *val, che permette di non scrivere esplicitamente   val[0],val[1],...
        cursor.execute(sql, *val)
        if i==20000:
            conn.commit()
            i=0
        
    cursor.close()
    conn.commit()

if __name__ == '__main__':
    server = 'lds.di.unipi.it'
    database = 'Group_16_DB'
    username = 'Group_16'
    password = 'M5CFTY1Z'
    connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password
    conn = pyodbc.connect(connectionString)

    #leggo i csv con DictReader
    geo = open('table/countries_new.csv', 'r')
    rgeo = csv.DictReader(geo, delimiter=',')
    date= open('table/date.csv', 'r')
    rdate= csv.DictReader(date, delimiter=',')
    tournament = open('table/tournament.csv', 'r')
    rtournament = csv.DictReader(tournament, delimiter=',')
    player = open('table/player.csv', 'r')
    rplayer = csv.DictReader(player, delimiter=',')
    match= open('table/match.csv', 'r')
    rmatch= csv.DictReader(match, delimiter=',')

    #inserisco nel database sul server
    insert(conn, rgeo, 'Geography')
    insert(conn, rdate, 'Date')
    insert(conn, rtournament, 'Tournament')
    insert(conn, rplayer, 'Player')
    insert(conn, rmatch, 'Match')

    #chiudo file e connessione
    geo.close()
    date.close()
    tournament.close()
    player.close()
    match.close()
    conn.close()