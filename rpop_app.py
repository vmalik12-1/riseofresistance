from flask import Flask, request, render_template, make_response
import pandas as pd
from app.main.rpob_rif import find_mutation, plot_heatmap, plot_heatmap_sns

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mutation = request.form.get("mutation") 
        
        #analyze
        results = find_mutation(mutation)
        #convert results to html
        mut_freq = results["mutation_frequency"]
        mut_loc = results["mutation_loc_frequency"]
        sources = results["sources"]
        plots = results["plots"]
        return render_template("results.html", mut_freq = mut_freq, mut_loc = mut_loc, sources=sources, plots=plots[0])
    
    init_analysis = plot_heatmap_sns()
    heatmap = init_analysis["heatmap"]
    return render_template("index.html", heatmap = heatmap)


if __name__ == "__main__":
    app.run(debug=True)