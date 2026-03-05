from app import db, create_app
from app.main.models import Mutation, Admin
import pandas as pd

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import os

app = create_app()
app.app_context().push()

db.create_all()

fname = "1801.csv"
try:
    df = pd.read_csv(fname) #create dataframe from csv file
except FileNotFoundError:
    print(f"error:  file '{fname}' not found, check path.")
    exit()

for _, row in df.iterrows():
    m = Mutation(aa_mut = row["Mutation"], 
                 bp_mut = row["Base pair change"], 
                 species = row["Bacteria of origin"],
                 source = row["Source"])
    db.session.add(m)
db.session.commit()

a = Admin(username = "vanya")
a.set_password("123")
db.session.add(a)
db.session.commit()


