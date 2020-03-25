### FOR POPULATING SQL QUERIES, TO TEST THE FILE UPLOAD FEATURE BECAUSE FOREIGN KEY MAKES IT NULL

from sqlalchemy import update

newToner = Toner(toner_id = 1,
                    toner_color = 'blue',
                    toner_hex = '#0F85FF')

dbsession.add(newToner)   
dbsession.flush()