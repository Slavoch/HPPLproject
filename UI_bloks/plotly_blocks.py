import numpy as np
import plotly.graph_objects as go
from trace_updater import TraceUpdater

from plotly_resampler import FigureResampler


def generate_fig(x, y, legend=None, title=None):
    fr = FigureResampler(go.Figure(), verbose=True)
    fr.add_trace(go.Scattergl(name=legend), hf_x=x, hf_y=y)
    fr.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation="h", y=1.12, xanchor="right", x=1),
        template="seaborn",
        title=title,
        title_x=0.5,
    )
    return fr
