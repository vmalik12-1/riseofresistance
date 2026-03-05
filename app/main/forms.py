from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class MutationForm(FlaskForm): 
    mutation = StringField('Enter mutation', validators = [DataRequired()])
    submit = SubmitField('Analyze')

class NewMutationForm(FlaskForm):
    aa_mutation = StringField('Amino acid change', validators = [DataRequired()])
    bp_mutation = StringField('Nucleotide change', validators = [DataRequired()])
    species = StringField('Species', validators = [DataRequired()])
    source = StringField('Source', validators = [DataRequired()])
    submit = SubmitField('Submit')
    
class ApproveForm(FlaskForm):
	submit = SubmitField('Approve')

class DenyForm(FlaskForm):
	submit = SubmitField('Deny')

class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
