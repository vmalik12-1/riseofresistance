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
    labels = [x.upper() for x in aa_s]
    mut_matrix = []
    loc_matrix = []
    aa_comb = []
    aa_locs = []

    mutations = db.session.scalars(sqla.select(Mutation)).all()

    for mutation in mutations:
        m = mutation.get_aa_mut().lower()
        if m[0] in aa_s and m[len(m) - 1] in aa_s:
            aa_comb.append([m[0], m[len(m) - 1]])
            m_loc_str = re.findall(r'\d+', m)
            m_loc = int(m_loc_str[0])
            aa_locs.append((m_loc, m[len(m) - 1]))

    all_locs = [aa_loc[0] for aa_loc in aa_locs]

    loc_min = min(all_locs)
    loc_max = max(all_locs)

    # create continuous range
    locs = list(range(loc_min, loc_max + 1))
    
    for aa_m in aa_s:
        freq = []
        for loc in locs:
            occurs = aa_locs.count((loc, aa_m))
            freq.append(occurs)
        loc_matrix.append(freq)
  
    loc_matrix_df = pd.DataFrame(loc_matrix, index=labels, columns=locs)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(
        loc_matrix_df,
        ax=ax,
        cmap="PuRd",
        annot=False,
        fmt="d",
        cbar_kws={"label": "Mutation Count", "shrink": 0.6},
        square=False,
    )

    ax.set_xticks(ax.get_xticks()[::5])

    ax.set_title("Heatmap of Single Amino Acid Substitution Mutations", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Amino Acid location", fontsize=12, labelpad=10)
    ax.set_ylabel("Mutated Amino Acid", fontsize=12, labelpad=10)
    ax.tick_params(axis="both", labelsize=10)

    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)

    init_analysis["heatmap"].append(base64.b64encode(buf.getvalue()).decode())


    for aa_m in aa_s:
        freq = []
        for aa_o in aa_s:
            occurs = aa_comb.count([aa_o, aa_m])
            freq.append(occurs)
        mut_matrix.append(freq)

    
    matrix_df = pd.DataFrame(mut_matrix, index=labels, columns=labels)

    fig, ax = plt.subplots(figsize=(6, 6))

    sns.heatmap(
        matrix_df,
        ax=ax,
        cmap="YlOrRd",
        annot=False,
        fmt="d",
        cbar_kws={"label": "Mutation Count", "shrink": 0.6},
        square=False,
    )

    ax.set_title("Heatmap of Single Amino Acid Substitution Mutations", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Original Amino Acid", fontsize=12, labelpad=10)
    ax.set_ylabel("Mutated Amino Acid", fontsize=12, labelpad=10)
    ax.tick_params(axis="both", labelsize=10)

    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)


    init_analysis["heatmap"].append(base64.b64encode(buf.getvalue()).decode())

    return init_analysis

