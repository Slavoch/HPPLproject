
import plotly.graph_objects as go
from plotly_resampler import FigureResampler
def generate_fig(x, y, legend=None, title=None):
    # Initialize FigureResampler with a Plotly Figure
    fr = FigureResampler(go.Figure(), verbose=True)

    # Add a scatter plot trace to the resampler
    # Use Scatter instead of Scattergl for standard scatter plot
    fr.add_trace(go.Scatter(name=legend, mode='markers'), hf_x=x, hf_y=y)

    # Update the layout of the figure
    fr.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation="h", y=1.12, xanchor="right", x=1),
        template="seaborn",
        title=title,
        title_x=0.5,
    )

    # Return the FigureResampler object
    return fr
