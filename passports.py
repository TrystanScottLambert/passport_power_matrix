"""
Hacky script to generate the passport power index matrix plot
(I know it's ugly)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

from rename import renames

ALPHABETICAL = (
    False  # Make True if you want alphabetical else it will be sorted by power rank.
)

# power rankings from passportindex.com
with open("power_rankings.html", encoding="utf8") as file:
    lines = file.readlines()

ranked_countries = [
    line.split("passport/")[1].split("/")[0].capitalize()
    for line in lines
    if line.strip() != ""  # ignore empty lines
]

corrected = []
for country in ranked_countries:
    if country in renames:
        corrected.append(renames[country])
    else:
        corrected.append(country)

# Prepare csv data
df = pd.read_csv("passport-index-matrix.csv")
df = df.set_index("Passport")

if ALPHABETICAL:
    df = df.sort_index(axis=0)
    df = df.sort_index(axis=1)
else:
    df = df.reindex(corrected, axis=0)
    df = df.reindex(corrected, axis=1)

df = df.drop("Vatican City", axis=0, errors="ignore")
df = df.drop("Vatican City", axis=1, errors="ignore")

# Coloring
categories = [
    "visa free",
    "visa on arrival",
    "eta",
    "e-visa",
    "visa required",
    "no admission",
]

cat_to_num = {cat: i for i, cat in enumerate(categories)}

DIAG_INDEX = len(categories)


def map_value(val, orig_val):
    """Creates a numerical value for each cell which can be applied to the plot"""
    if orig_val == "-1":
        return DIAG_INDEX
    try:
        _ = int(val)
        return cat_to_num["visa free"]
    except:
        pass
    return cat_to_num.get(val, np.nan)  # NaN for unexpected entries


numeric_df = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
for r in df.index:
    for c in df.columns:
        numeric_df.at[r, c] = map_value(df.at[r, c], df.at[r, c])

colors = [
    "#0000FF",  # visa free - blue (least restrictive)
    "#00C3FF",  # visa on arrival - lighter blue
    "#00FF33",  # eta - even lighter blue
    "#EEFF00",  # e-visa - lighter still
    "#F40C0C",  # visa required - red (most restrictive)
    "#000000",  # no admission - bright red (most restrictive)
]
colors.append("#FFFFFF")  # black for diagonal

cmap = ListedColormap(colors)

bounds = np.arange(-0.5, len(categories) + 1.5, 1)
norm = BoundaryNorm(bounds, cmap.N)


# Plot figure
plt.figure(figsize=(20, 18), dpi=800)
ax = sns.heatmap(
    numeric_df,
    cmap=cmap,
    norm=norm,
    cbar_kws={
        "ticks": np.arange(len(categories) + 1),
        "label": "Visa Status",
        "shrink": 0.5,
    },
    linewidths=0.1,
    linecolor="gray",
)

# Set tick labels to all country names, rotated for readability
ax.set_xticks(np.arange(len(numeric_df.columns)) + 0.5)
ax.set_xticklabels(numeric_df.columns, rotation=90, fontsize=6)
ax.set_yticks(np.arange(len(numeric_df.index)) + 0.5)
ax.set_yticklabels(numeric_df.index, rotation=0, fontsize=6)

colorbar = ax.collections[0].colorbar
colorbar.set_ticks(np.arange(len(categories) + 1))
colorbar.set_ticklabels(categories + ["Same Country"])

plt.title("Visa Status Matrix", fontsize=18)
plt.xlabel("Destination Country")
plt.ylabel("Passport Country")
plt.figtext(
    0.01,
    0.01,
    "github.com/TrystanScottLambert/passport_power_matrix",
    fontsize=5,
    color="gray",
    alpha=0.5,
    ha="left",
    va="bottom",
)
plt.tight_layout()
if ALPHABETICAL:
    plt.savefig("passport_power_matrix_alphabetical.png")
else:
    plt.savefig("passport_power_matrix_powerranked.png")
plt.close()
