from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
import sqlalchemy as sqla
from app.main.models import NewMutation, Mutation
from app.main.forms import ApproveForm, DenyForm, EmptyForm, MutationForm, NewMutationForm
from flask_login import login_required
from sqlalchemy import text
from app.main.rpob_rif import find_mutation, plot_heatmap_sns

from app.main import main_blueprint as main

@main.route("/", methods=["GET"])
@main.route('/index', methods=['GET'])
def index():
    init_analysis = plot_heatmap_sns()
    heatmap = init_analysis["heatmap"]
    mutations = db.session.scalars(sqla.select(Mutation)).all()
    return render_template("index.html", heatmap = heatmap, mutations = mutations)

@main.route('/analyze', methods=['GET', 'POST'])
def analyze_mutation():
    mForm = MutationForm()
    if mForm.validate_on_submit(): #returns true only if there is a post request recieved and if all data in the form is validated
        mutation = mForm.mutation.data
        return redirect(url_for('main.mutation_results', mutation=mutation)) #returns url of endpoint for this function
    return render_template("analyze_mutation.html", form = mForm)

@main.route('/contribute', methods=['GET', 'POST'])
def submit_request():
    mForm = NewMutationForm()
    if mForm.validate_on_submit(): #returns true only if there is a post request recieved and if all data in the form is validated
        new_mutation = NewMutation(aa_mut = mForm.aa_mutation.data, 
                                   bp_mut = mForm.bp_mutation.data,
                                   species = mForm.species.data,
                                   source = mForm.source.data)
        db.session.add(new_mutation)
        db.session.commit()
        flash('Request submitted')
        return redirect(url_for('main.index')) #returns url of endpoint for this function
    return render_template("enter_mut.html", form = mForm)

@main.route("/results/<string:mutation>/", methods = ['GET'])
def mutation_results(mutation):
     #analyze
    results = find_mutation(mutation)
    #convert results to html
    mut_freq = results["mutation_frequency"]
    mut_loc = results["mutation_loc_frequency"]
    sources = results["sources"]
    plots = results["plots"]
    all_mutations = db.session.scalars(sqla.select(Mutation)).all()
    return render_template("results.html", mut_freq = mut_freq, mut_loc = mut_loc, sources=sources, plots=plots[0], mutation = mutation.upper(), mutations = all_mutations)

@main.route("/admin/requests/", methods = ['GET', 'POST'])
@login_required
def view_requests():
    mutation_requests = db.session.scalars(sqla.select(NewMutation)).all()
    aform = ApproveForm()
    dform = DenyForm()
    return render_template('mutation_requests.html', mutation_requests = mutation_requests, aform = aform, dform = dform)

@main.route("/admin/requests/<int:new_mutation_id>/accept", methods = ['POST'])
@login_required
def accept_request(new_mutation_id):
    new_m = db.session.scalars(sqla.select(NewMutation).where(NewMutation.id == new_mutation_id)).first()
    if new_m is None:
        flash("Request not found.")
        return redirect(url_for('main.view_requests'))
    aform = ApproveForm()
    dform = DenyForm()
    if aform.validate_on_submit():
        m = Mutation(aa_mut = new_m.get_aa_mut(), bp_mut = new_m.get_bp_mut(), species = new_m.get_species(), source = new_m.get_source())
        db.session.add(m)
        db.session.delete(new_m)
        db.session.commit()
        flash("Mutation request approved.")
        return redirect(url_for('main.index'))
    mutation_requests = db.session.scalars(sqla.select(NewMutation)).all()
    return render_template('mutation_requests.html', mutation_requests = mutation_requests, aform = aform, dform = dform)

@main.route("/admin/requests/<int:new_mutation_id>/deny", methods = ['POST'])
@login_required
def deny_request(new_mutation_id):
    new_m = db.session.scalars(sqla.select(NewMutation).where(NewMutation.id == new_mutation_id)).first()
    if new_m is None:
        flash("Request not found.")
        return redirect(url_for('main.view_requests'))
    aform = ApproveForm()
    dform = DenyForm()
    if dform.validate_on_submit():
        db.session.delete(new_m)
        db.session.commit()
        flash("Mutation request denied.")
        return redirect(url_for('main.index'))
    mutation_requests = db.session.scalars(sqla.select(NewMutation)).all()
    return render_template('mutation_requests.html', mutation_requests = mutation_requests, aform = aform, dform = dform)

