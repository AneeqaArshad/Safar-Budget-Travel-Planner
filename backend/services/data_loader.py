import pandas as pd

from models.city import City
from models.place import Place
from extensions import db

def load_csv_data():

    if Place.query.count()>0:
        return

    df = pd.read_csv("data/places.csv")

    cities={}

    for city_name in df["city"].unique():

        city=City(name=city_name)

        db.session.add(city)

        db.session.flush()

        cities[city_name]=city.id


    for _,row in df.iterrows():

        place=Place(

            name=row["name"],

            city_id=cities[row["city"]],

            category=row["category"],

            cost=row["cost"],

            popularity=row["popularity"],

            description=row["description"],

            rating=row["rating"],

            time_required=row["time_required"],

            best_time=row["best_time"],

            image_url=row.get("image_url")
        )

        db.session.add(place)

    db.session.commit()