import csv
from datetime import datetime, date, timedelta  


#funzione che va a scrivere i dati nel file csv match
def selectValueMatch(row, writer):
    if (row['match_num'] == '' or row['tourney_id'] ==''):
        print("MISS VALUE IN MATCH_NUM O IN TOURNEY_ID")
    row.update({'match_id': row['match_num']+ row['tourney_id']})
    writer.writerow(row)
    
    
  
    
#funzione che va a scrivere i dati nel file csv Tournament
def selectValueTournament(row, distinctValue, writer):
    row.update({'date_id': row['tourney_date']})
    KeySelected=row['tourney_id']

    #controllo che i duplicati su tourney_id (che non vengono inseriti) presentano valori diversi
    if KeySelected in distinctValue:
        rowSelected=distinctValue[KeySelected]
        for key in writer.fieldnames:
            if (row[key] != rowSelected[key]):
                print("Errore: torneo con id " + KeySelected + ' ha diversi valori su '+key+' '+row[key]+ ' '+rowSelected[key])
    
    #se invece la chiave non è presente, la vado a scrivere nel file e in distinctValue
    else:
        #salvo in distinctValue con key tourney_id e value un dizionario contenente tutti gli attributi in fieldnames
        rowTournament=dict()
        for attr in writer.fieldnames:
            rowTournament[attr]=row[attr]
        distinctValue[KeySelected]=rowTournament
        writer.writerow(row)
 
    
#funzione che va a scrivere i dati nel file csv Date
def selectValueData(row, distinctValue, writer):
    KeySelected=row['date_id']
    
    #controllo di non aver gia inserito il valore della chiave, qui non importa il controllo per gli errori:
    #gli altri campi derivano dal valore della chiave
    if KeySelected not in distinctValue:
        rowDate=dict()
        rowDate['date_id']=KeySelected

        #recupero giorno, mese, anno e quarter dalla data.
        #con strptime creo un object datetime partendo da una stringa e poi lo formatto con strftime
        rowDate['year'] = datetime.strptime(KeySelected, '%Y%m%d').strftime('%Y')
        rowDate['month']= datetime.strptime(KeySelected, '%Y%m%d').strftime('%B')
        rowDate['day']= datetime.strptime(KeySelected, '%Y%m%d').strftime('%A')
        rowDate['quarter']= 'Q'+ str(int((int(datetime.strptime(KeySelected, '%Y%m%d').strftime('%m')) +2)/3))
        #inserisco in distinctValue il dizionario con key date_id
        distinctValue[KeySelected]=rowDate
        writer.writerow(rowDate)
        
        
        
#funzione che va a scrivere i dati nel file csv Player.
#maleSet e femaleSet sono due set utilizzati dalla funzione per recuperare il sesso di un player in base al nome.
#La ricerca ha costo computazionale essendo il set hashato
def selectValuePlayer(row, distinctValue, writer, maleSet, femaleSet):

    players=['winner','loser']
    for player in players:
        #recupero l'id del player (winner o loser)
        KeySelected=row[player+'_id']

        #controllo se il player è già presente nel file di output e che non abbia valori diversi sugli attributi
        if KeySelected in distinctValue:
            rowSelected=distinctValue[KeySelected]
            for key in writer.fieldnames:
                if key == ('name')  and (row[player+'_'+key] != rowSelected[key]):
                    print("Errore: player con id " + KeySelected + ' ha diversi valori su '+key+' '+row[player+'_'+key]+ ' '+rowSelected[key])
                elif key == ('ioc') and (row[player+'_'+key] != rowSelected[key]):
                     print("Errore: player con id " + KeySelected + ' ha diversi valori su '+key+' '+row[player+'_'+key]+ ' '+rowSelected[key])
                elif key == ('hand')  and (row[player+'_'+key] != rowSelected[key]):
                     print("Errore: player con id " + KeySelected + ' ha diversi valori su '+key+' '+row[player+'_'+key]+ ' '+rowSelected[key])
                elif key == ('ht')  and (row[player+'_'+key] != rowSelected[key]):
                     print("Errore: player con id " + KeySelected + ' ha diversi valori su '+key+' '+row[player+'_'+key]+ ' '+rowSelected[key])

                #controllo che l'anno di nascita di row calcolato rispetto alla data del torneo combaci con quello già presente
                elif key == ('year_of_birth'):
                    newRowYear=annoNascita(row['tourney_date'],row[player+'_age'])
                    oldRowYear=rowSelected['year_of_birth']
                    if newRowYear!=oldRowYear and newRowYear!='':
                        print("Errore: player con id " + KeySelected + rowSelected['name']+' ha diversi valori su '+key+' nuovo = '+
                              str(newRowYear) +' vecchio = '+str(oldRowYear)+ ' con data torneo '+ row['tourney_date'])
                else:
                     continue
        else:
            #se invece non è ancora presente lo scrivo nel file e aggiorno distinctValue
            rowPlayer=dict()
            rowPlayer['player_id']=KeySelected
            rowPlayer['country_id'] = row[player+'_ioc']
            rowPlayer['name']= row[player+'_name']
            rowPlayer['hand']= row[player+'_hand']
            rowPlayer['ht']= row[player+'_ht']
            
            #controllo se il player con questo nome è nel set dei maschi o in quello delle femmine
            if (rowPlayer['name']) in maleSet:
                rowPlayer['sex']= 'male'
                
            elif (rowPlayer['name']) in femaleSet:
                rowPlayer['sex']= 'female'
            else:
                print('player con name '+rowPlayer['name']+' non ha sesso')
                rowPlayer['sex']= ''

            #calcolo l'anno di nascita del giocatore
            rowPlayer['year_of_birth']= annoNascita(row['tourney_date'],row[player+'_age'])
            
            #non inserisco row se il valore su year_of_birth è null.
            #inserirò il prossimo con anno di nascita!= null
            if rowPlayer['year_of_birth']=='':
                continue
            else:
                #inserisco il dizionario creato in distinctValue e lo vado a scrivere nel file
                distinctValue[KeySelected]=rowPlayer
                writer.writerow(rowPlayer)

    
#funzione che restituisce l'anno di nascita.
#a partire dall'età in float del player ad una certa data calcolo il giorno del compleanno del giocatore
#moltiplicando la parte decimale per 365 e sottraendo i giorni ottenuti dalla data del torneo.
#a questo punto estraggo l'anno di nascita dalla data del compleanno del giocatore
def annoNascita(dataTorneo, etaDuranteTorneo):
    
    #restituisce null se la data del torneo o l'età sono valori null
    if (dataTorneo=='' or etaDuranteTorneo==''):
        return ''
    
    else:
        annoTorneo = datetime.strptime(dataTorneo, '%Y%m%d').strftime('%Y')
        meseTorneo=datetime.strptime(dataTorneo, '%Y%m%d').strftime('%m')
        giornoTorneo=datetime.strptime(dataTorneo, '%Y%m%d').strftime('%d')
        dateTorneo = date(int(annoTorneo), int(meseTorneo), int(giornoTorneo))

        anniPlayer=int(float(etaDuranteTorneo))
        frazioneEtaPlayer=float(etaDuranteTorneo) - anniPlayer
        giorniTraCompleannoTorneo=int(frazioneEtaPlayer*365)

        dateBirthday=dateTorneo - timedelta(days=(giorniTraCompleannoTorneo) )
        result = dateBirthday.strftime("%Y")
        result=int(result) -anniPlayer
        
        return result
    
#funzione che creare il set di player a partire dal reader
#vengono concatenati nome e cog
def createSetPlayer(file):
    
    setPlayer=set()
    for row in file:
        value=''
        for attr in row:
            value=value+row[attr]+' '
        value=value[:-1]
        setPlayer.add(value)
        
    return setPlayer


if __name__ == '__main__':
    #percorsi file di input
    tennis_file='data/tennis_new.csv'
    male_file='data/male_new.csv'
    female_file='data/female_new.csv'

    #percorsi file di output
    match_file='table/match.csv'
    tournament_file='table/tournament.csv'
    player_file='table/player.csv'
    date_file='table/date.csv'
    
    
    #definisco i nomi degli attributi dei 5 file csv che saranno creati
    header_match = ['tourney_id', 'match_id', 'winner_id', 'loser_id', 'score', 'best_of', 'round', 'minutes', 'w_ace',
              'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced', 'l_ace',
              'l_df', 'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_SvGms', 'l_bpSaved', 'l_bpFaced', 'winner_rank',
              'winner_rank_points', 'loser_rank', 'loser_rank_points']
    header_tournament = ['tourney_id', 'date_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level',
                   'tourney_spectators', 'tourney_revenue']
    header_player = ['player_id', 'country_id', 'name', 'sex', 'hand', 'ht', 'year_of_birth']
    header_date = ['date_id', 'day', 'month', 'year', 'quarter']
    header_country=['country_ioc','continent','language']

    #apro i file csv
    tennis= open(tennis_file, 'r')
    male= open(male_file, 'r')
    female= open(female_file, 'r')

    #utilizzo il DictReader per leggere il csv
    #ogni riga sarà un dizionario con chiave=attributo e valore=valore della riga su quell'attributo
    rtennis= csv.DictReader(tennis, delimiter=',')
    rMale= csv.DictReader(male, delimiter=',')
    rFemale= csv.DictReader(female, delimiter=',')
    
    #creo due set contenenti male e female
    maleSet=createSetPlayer(rMale)
    femaleSet=createSetPlayer(rFemale)

    #apro i 5 file csv dove andrò a scrivere i dati
    match= open(match_file, 'w', newline='')
    tournament= open(tournament_file, 'w', newline='')
    player= open(player_file, 'w', newline='')
    data = open(date_file, 'w', newline='')

    #utilizzo il DictWriter per scrivere i csv
    #in fieldnames va specificato l'header del csv in output
    #con extrasaction ignore vengono ignorati in scrittura gli attributi in più rispetto a fieldnames
    wmatch= csv.DictWriter(match, delimiter=',', fieldnames=header_match, extrasaction='ignore')
    wtournament = csv.DictWriter(tournament, delimiter=',', fieldnames=header_tournament, extrasaction='ignore')
    wplayer = csv.DictWriter(player, delimiter=',', fieldnames=header_player, extrasaction='ignore')
    wdate = csv.DictWriter(data, delimiter=',', fieldnames=header_date, extrasaction='ignore')

    #scrivo gli header nei csv
    writers = [wmatch, wtournament, wdate, wplayer]
    for w in writers:
        w.writeheader()

    #mantengo i valori distinti sulla primary key in dizioniari
    tournament_distinct=dict()
    player_distinct=dict()
    date_distinct=dict()
    country_distinct=dict()
    
    #itero su tennis e scrivo nei csv di output
    for row in rtennis:
        selectValueMatch(row, wmatch)
        selectValueTournament(row, tournament_distinct, wtournament)
        selectValuePlayer(row, player_distinct, wplayer, maleSet, femaleSet)
        selectValueData(row, date_distinct, wdate)



    #chiudo tutti file aperti in lettura
    tennis.close()
    male.close()
    female.close()
    
    #chiudo tutti file aperti in scrittura
    match.close()
    tournament.close()
    data.close()
    player.close()


