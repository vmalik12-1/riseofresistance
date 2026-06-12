from app import db, create_app
from app.main.models import Mutation, Admin
import pandas as pd

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from dotenv import load_dotenv
import os

load_dotenv()
app = create_app()
app.app_context().push()
db.drop_all()
print("Before create_all")
db.create_all()
print("After create_all")

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

admin_exists = db.session.scalars(sqla.select(Admin).where(Admin.username == 'vanya')).first()
if not admin_exists:
    a = Admin(username = os.getenv("ADMIN_USER"))
    a.set_password(os.getenv("ADMIN_PASSWORD"))
    db.session.add(a)
    db.session.commit()

print("DONE")


