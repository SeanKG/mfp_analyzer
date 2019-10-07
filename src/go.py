import myfitnesspal
import sqlite3
import datetime

db = sqlite3.connect("mydb.db")
cursor = db.cursor()
cursor.execute('''
    DROP TABLE diary;
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS diary(
        date DATE PRIMARY KEY,
        calories INTEGER,
        carbohydrates INTEGER,
        fat INTEGER,
        protein INTEGER
        )
''')
db.commit()

client = myfitnesspal.Client('seakeg')

days = 90
# today = 

date = datetime.datetime.now()

# date

while days > 0:
    days-= 1
    # load a single day
    day = client.get_date(date.year, date.month, date.day)
    # add to db
    calories = day.totals.get('calories')
    carbohydrates = day.totals.get('carbohydrates')
    fat = day.totals.get('fat')
    protein = day.totals.get('protein')

    cursor.execute('''
        INSERT INTO diary(date, calories, carbohydrates, fat, protein)
        VALUES(:date,:calories,:carbohydrates,:fat,:protein)
    ''', {'date': date,'calories': calories,'carbohydrates': carbohydrates,'fat': fat,'protein': protein})
        # ON CONFLICT(date) DO UPDATE SET
        #     calories=excluded.calories,
        #     carbohydrates=excluded.carbohydrates,
        #     fat=excluded.fat,
        #     protein=excluded.protein;
    
    db.commit()
    print(date)
    date-= datetime.timedelta(days=1)

db.close()
