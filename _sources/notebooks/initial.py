# %% [markdown]
"""
# Initial exploration of the data
"""

# %% tags=['hide-cell']
from IPython import get_ipython

if get_ipython() is not None:
    get_ipython().run_line_magic("load_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "2")

# %%
import pandas as pd
from babytimes import data as d
from pygsutils import general as g
import altair as alt

# %%
st = d.Sleeptimes({"loc": "./../../data"})

# %%
st.df_viz.head()

# %%
bars = alt.Chart(st.df_viz).mark_bar().encode(
    y="yearmonthdate(begin)",
    x="hoursminutesseconds(begin)",
    x2="hoursminutesseconds(end)",
)