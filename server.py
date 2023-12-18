from uuid import uuid4

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import (
    MATCH,
    ALL,
    Input,
    Output,
    State,
    callback_context,
    dcc,
    html,
    no_update,
)
from dash_extensions.enrich import (
    DashProxy,
    Serverside,
    ServersideOutputTransform,
    Trigger,
    TriggerTransform,
)
from trace_updater import TraceUpdater

from plotly_resampler import FigureResampler
import re
from UI_bloks.plotly_blocks import generate_fig


def run_UI_server(server, data):
    # --------------------------------------Globals ---------------------------------------
    app = DashProxy(
        __name__,
        server=server,
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.LUX],
        transforms=[ServersideOutputTransform(), TriggerTransform()],
    )

    # -------- Construct the app layout --------
    app.layout = html.Div(
        [
            html.Div(html.H1("Dash application"), style={"textAlign": "center"}),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Form(
                            [
                                dbc.Label("port id", style={"margin-left": "10px"}),
                                html.Br(),
                                dcc.Input(
                                    id="input-port-connect",
                                    placeholder="n",
                                    type="number",
                                    style={"margin-left": "10px"},
                                ),
                                *([html.Br()] * 2),
                                dbc.Button(
                                    "Connect new port",
                                    id="connect-port-btn",
                                    color="primary",
                                    style={
                                        "textalign": "center",
                                        "width": "max-content",
                                        "margin-left": "10px",
                                    },
                                ),
                                *([html.Br()] * 2),
                                dbc.Label("port id", style={"margin-left": "10px"}),
                                html.Br(),
                                dcc.Input(
                                    id="nbr-datapoints",
                                    placeholder="n",
                                    value=1000,
                                    type="number",
                                    style={"margin-left": "10px"},
                                ),
                                *([html.Br()] * 2),
                                dbc.Button(
                                    "Create new graph",
                                    id="add-graph-btn",
                                    color="primary",
                                    style={
                                        "textalign": "center",
                                        "width": "max-content",
                                        "margin-left": "10px",
                                    },
                                ),
                                *([html.Br()] * 2),
                            ],
                        ),
                        style={"align": "top"},
                        md=2,
                    ),
                    dbc.Col(html.Div(id="graph-container"), md=10),
                ],
            ),
        ]
    )

    # ------------------------------------ DASH logic -------------------------------------
    # This method adds the needed components to the front-end, but does not yet contain the
    # FigureResampler graph construction logic.
    @app.callback(
        Output("graph-container", "children"),
        Input("add-graph-btn", "n_clicks"),
        Input({"type": "remove-graph-btn", "index": ALL}, "n_clicks"),
        [
            State("nbr-datapoints", "value"),
            State("graph-container", "children"),
            State({"type": "remove-graph-btn", "index": ALL}, "id"),
        ],
        prevent_initial_call=True,
    )
    def add_or_remove_graph(
        add_graph, remove_graph, port_id, gc_children, remove_btn_id
    ):
        #### check of existance such data with demanded port ####
        try:
            data[str(port_id)]
        except KeyError as e:
            return no_update

        #### Remove graph ####

        gc_children = [] if gc_children is None else gc_children

        clicked_btn = callback_context.triggered[0]["prop_id"].split(".")[0]
        if "remove-graph" in clicked_btn:
            if not len(gc_children):
                return no_update
            new_children = []
            btn_index = re.search('"index":"(.*)",', clicked_btn).group(1)
            for child in gc_children:
                if child["props"]["id"]["index"] != btn_index:
                    new_children.append(child)
            return new_children

        #### create a new graph ####
        if add_graph is None or port_id is None:
            return no_update

        uid = str(uuid4())
        new_child = html.Div(
            id={"type": "dynamic-graph-container", "index": uid},
            children=[
                dcc.Graph(
                    id={"type": "dynamic-graph", "index": uid}, figure=go.Figure()
                ),
                dcc.Loading(dcc.Store(id={"type": "store", "index": uid})),
                TraceUpdater(
                    id={"type": "dynamic-updater", "index": uid}, gdID=f"{uid}"
                ),
                dcc.Interval(
                    id={"type": "interval", "index": uid}, max_intervals=1, interval=1
                ),
                dcc.Interval(
                    id={"type": "interval-data-update", "index": uid},
                    interval=2000,  # im ms
                    n_intervals=0,
                ),
                dbc.Button(
                    "Remove graph",
                    id={"type": "remove-graph-btn", "index": uid},
                    color="danger",
                    style={
                        "textalign": "center",
                        "width": "max-content",
                        "margin-left": "10px",
                    },
                ),
            ],
        )
        gc_children.append(new_child)
        return gc_children

    ##------------------------------- Update data in graph --------------------------------------##
    @app.callback(
        Output(
            {"type": "dynamic-graph", "index": MATCH}, "figure", allow_duplicate=True
        ),
        Input({"type": "interval-data-update", "index": MATCH}, "n_intervals"),
        State({"type": "dynamic-graph", "index": MATCH}, "id"),
        # State({"type": "dynamic-graph", "index": MATCH}, "figure"),
        prevent_initial_call=True,
    )
    def update_data_in_graph(n_intervals, id):
        data_pointer = None

        for port_id in data.keys():
            if id["index"] in data[port_id]["active_in"]:
                data_pointer = data[port_id]
                break
        if data_pointer is None:
            raise Exception("LOOOL")

        x = data_pointer["x"]
        y = data_pointer["y"]

        fr = generate_fig(x, y)
        Serverside(fr)
        return fr

    ##-------------------------------- FOR plotly resample updates ------------------------------##
    # This method constructs the FigureResampler graph and caches it on the server side
    @app.callback(
        Output({"type": "dynamic-graph", "index": MATCH}, "figure"),
        Output({"type": "store", "index": MATCH}, "data"),
        State("nbr-datapoints", "value"),
        # State("add-graph-btn", "n_clicks"),
        State({"type": "dynamic-graph", "index": MATCH}, "id"),
        Trigger({"type": "interval", "index": MATCH}, "n_intervals"),
        prevent_initial_call=True,
    )
    def construct_display_graph(port_id, container_id) -> FigureResampler:
        ## save index of active containers in data
        container_index = container_id["index"]
        data_index = str(port_id)
        data[data_index]["active_in"].append(container_index)

        ## generate gfaph from data
        port_data = data[data_index]
        x = port_data["x"]
        y = port_data["y"]
        fr = generate_fig(x, y)
        return fr, Serverside(fr)

    @app.callback(
        Output({"type": "dynamic-updater", "index": MATCH}, "updateData"),
        Input({"type": "dynamic-graph", "index": MATCH}, "relayoutData"),
        State({"type": "store", "index": MATCH}, "data"),
        prevent_initial_call=True,
        memoize=True,
    )
    def update_fig(relayoutdata: dict, fig: FigureResampler):
        if fig is not None:
            return fig.construct_update_data(relayoutdata)
        return no_update

    # --------------------------------- Running the app ---------------------------------
    app.run_server(debug=True, port=9023)
