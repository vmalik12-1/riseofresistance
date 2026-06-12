import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
import io
from collections import Counter
from app.main.models import Mutation
import seaborn as sns
import sqlalchemy as sqla
from app import db
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fname = "1801.csv" 
aa_s = ["a", "g", "l", "i", "v", "m", "p", "c", "s", "t", "q", "n", "h", "k", "r", "d", "e", "f", "w", "y"]


def find_mutation(the_mutation):

    mut = the_mutation.lower()
    print(f"your mutation is {mut}")
    mut_loc = re.findall(r'\d+', mut)
    print(f"mutation location is {mut_loc}")
    loc_occ = 0
    occs = 0
    sources = []
    bp_mut = []
    aa_comb = []
    mutations = db.session.scalars(sqla.select(Mutation)).all()
    for mutation in mutations:
        print(mutation.get_aa_mut())
        m = mutation.get_aa_mut().lower()
        if m[0] in aa_s and m[len(m) - 1] in aa_s:
            aa_comb.append([m[0], m[len(m) - 1]])
        source = mutation.get_source()
        bp_change = mutation.get_bp_mut()
        if mut == m:
            occs += 1
            sources.append(source)
            bp_mut.extend([c.strip() for c in bp_change.split(",")])

        m_loc = re.findall(r'\d+', m)
        if set(m_loc).issubset(set(mut_loc)):
            loc_occ += 1
            sources.append(source)
    
    
    
    results = {
        "mutation_frequency": [],
        "mutation_loc_frequency": [],
        "sources": [],
        "heatmap": [],
        "plots": []
    }

    results["mutation_frequency"] = occs
    results["mutation_loc_frequency"] = loc_occ
    results["sources"] = list(set(sources))
    results["plots"].append(plot_pie_chart(bp_mut))


    print(f"Your specific mutation occurred {occs} times.")
    print(f"Your mutation location occurred {loc_occ} times.")
    return results

def plot_pie_chart(bp_mut):

    # Count frequencies from list
    counts = Counter(bp_mut)

    if not counts:
        return None

    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    changes, frequencies = zip(*sorted_items)

    total = sum(frequencies)
    percentages = [freq / total * 100 for freq in frequencies]

    colors = plt.cm.Set3.colors

    plt.figure(figsize=(4,4))

    wedges, texts, autotexts = plt.pie(
        percentages,
        labels=[f"{change[0]}-->{change[len(change) - 1]}" if change != "unk" else "Unknown" for change in changes],   # <-- show AT, GC, etc.
        startangle=90,
        counterclock=False,
        autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
        pctdistance=0.8,
        labeldistance=1.1,
        wedgeprops={'width':0.4, 'edgecolor':'white'},
        colors=colors
    )

    plt.title("Nucleotide changes involved in mutation", fontsize=14)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)

    return base64.b64encode(buf.getvalue()).decode()

def plot_heatmap_sns():
    init_analysis = {
        "heatmap": []
    }
    aa_labels = [x.upper() for x in aa_s]
    mut_matrix = []
    loc_matrix = []
    aa_comb = []
    aa_locs = []
    id_aa_matrix = []
    id_loc_matrix = []

    mutations = db.session.scalars(sqla.select(Mutation)).all()

    for mutation in mutations:
        m = mutation.get_aa_mut().lower()
        if m[0] in aa_s and m[len(m) - 1] in aa_s:
            aa_comb.append([m[0], m[len(m) - 1]])
            id_aa_matrix.append(mutation.get_mut_id())
            m_loc_str = re.findall(r'\d+', m)
            m_loc = int(m_loc_str[0])
            aa_locs.append((m_loc, m[len(m) - 1]))
            id_loc_matrix.append(mutation.get_mut_id())

    all_locs = [aa_loc[0] for aa_loc in aa_locs]

    loc_min = min(all_locs) - 10
    loc_max = max(all_locs) + 10

    # create continuous range
    locs = list(range(loc_min, loc_max + 1))
    

    mutant_id_loc_matrix = []
    for aa_m in aa_s:
        freq = []
        mutant_ids_per_row = []
        for loc in locs:
            occurs = aa_locs.count((loc, aa_m))
            if occurs > 0:
                mutant_ids_per_row.append(find_mutation_ids_loc(loc,aa_m))
            else:
                mutant_ids_per_row.append("No mutants")
            freq.append(occurs)
        loc_matrix.append(freq)
        mutant_id_loc_matrix.append(mutant_ids_per_row)
  
    loc_matrix_df = pd.DataFrame(loc_matrix, index=aa_labels, columns=locs)

    
   
    mutant_id_aa_matrix = []
    for aa_m in aa_s:
        freq = []
        mutant_ids_per_row = []
        for aa_o in aa_s:
            occurs = aa_comb.count([aa_o, aa_m])
            if occurs > 0:
                mutant_ids_per_row.append(find_mutation_ids_aa(aa_o,aa_m))
            else:
                mutant_ids_per_row.append("No mutants")
            freq.append(occurs)
        mut_matrix.append(freq)
        mutant_id_aa_matrix.append(mutant_ids_per_row)

    
    matrix_df = pd.DataFrame(mut_matrix, index=aa_labels, columns=aa_labels)

    #make plotly subplots
    plotly_fig = make_subplots(rows=2, cols=1, subplot_titles=("Mutation loci", "Amino acid substitutions"), vertical_spacing=0.10)
    my_config = {'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'resetScale', 'zoomIn', 'zoomOut'], 'displayModeBar': True}
    loc_x_labels = locs
    plotly_fig.add_trace(go.Heatmap(
        x=loc_x_labels,
        y=aa_labels,
        z=loc_matrix_df,
        xgap=0.1,
        ygap=1,
        customdata=mutant_id_loc_matrix,
        hovertemplate=("Locus: %{x} <br>" + "Mutated AA: %{y} <br>" + "IDs: %{customdata}<extra></extra>"),
        colorscale='Blues',
        colorbar=dict(
        thickness=15,
        len=0.45, 
        orientation="v",
        y=0.78,
        yanchor="middle"
    )
    ), row=1, col=1)

    plotly_fig.add_trace(go.Heatmap(
        x=aa_labels,
        y=aa_labels,
        z=matrix_df,
        customdata=mutant_id_aa_matrix,
        hovertemplate=("Original AA: %{x} <br>" + "Mutated AA: %{y} <br>" + "IDs: %{customdata}<extra></extra>"),
        xgap=1,
        ygap=1,
        colorscale=[
            [0.0,  "#FBF8F2"],
            [0.15, "#F5E6D8"],
            [0.35, "#EDCBBF"],
            [0.55, "#D9A3A8"],
            [0.75, "#C07A90"],
            [1.0,  "#9A5475"],
        ],
        colorbar=dict(
        thickness=15,
        len=0.45,         # spans the height of the bottom subplot
        orientation="v",
        y=0.22,           # centers on the bottom subplot
        yanchor="middle"
    ) 
    ), row=2,col=1)

    #first subplot (col 1)
    
    plotly_fig.update_xaxes(title_text="Amino Acid Location", range=[loc_min, loc_max],minallowed=loc_min, 
                            maxallowed=loc_max, constrain="domain", row=1, col=1)
    plotly_fig.update_yaxes(title_text="Substituted Amino Acid", constrain="domain", gridcolor="black", row=1, col=1)

    #second subplot (col 2)
    plotly_fig.update_xaxes(title_text="Original Amino Acid", row=2, col=1)
    plotly_fig.update_yaxes(title_text="Substituted Amino Acid", row=2, col=1)

    plotly_fig.update_layout(
    title={
        "text": "Frequencies of Amino Acid Mutations",
        "x": 0.5,
        "xanchor": "center",
        "font": {
            "size": 28,
            "family": "Arial, sans-serif"
        }
    })
    html_string = plotly_fig.to_html(full_html = False, config=my_config, include_plotlyjs='cdn')


    init_analysis["heatmap"].append(html_string)

    """ print(f"DEBUG: heatmap[0] length: {len(init_analysis['heatmap'][0])}")
    print(f"DEBUG: aa_comb sample: {aa_comb[:10]}")
    print(f"DEBUG: aa_comb length: {len(aa_comb)}")
    print(f"DEBUG: mut_matrix sum: {sum(sum(row) for row in mut_matrix)}") """
    return init_analysis

def find_mutation_ids_loc(loc, mutated_aa):
    back_mutation = f"{loc}{mutated_aa}".lower()
    mutants = db.session.scalars(sqla.select(Mutation).where(Mutation.aa_mut.ilike(f"%{back_mutation}"))).all()
    mutant_ids = []
    for mutant in mutants:
        mutant_ids.append(mutant.get_mut_id())
    return mutant_ids

def find_mutation_ids_aa(original_aa, mutated_aa):
    mut = db.session.scalars(sqla.select(Mutation).where(Mutation.id==1)).all()
    mutants = db.session.scalars(sqla.select(Mutation).where(Mutation.aa_mut.startswith(original_aa.upper())
                                                             & Mutation.aa_mut.endswith(mutated_aa.upper()))).all()
    mutant_ids = []
    for mutant in mutants:
        mutant_ids.append(mutant.get_mut_id())
    
    return mutant_ids

    


