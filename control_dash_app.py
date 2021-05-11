import dash
import random
import time
from pymemcache.client import base 
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


app = dash.Dash(__name__)

def rotate(x, y, z, theta):
    w = x + 1j * y
    return np.real(np.exp(1j * theta) * w), np.imag(np.exp(1j * theta) * w), z

def rotate_z(x, y, z, theta):
    w = x + 1j * y
    return np.real(np.exp(1j * theta) * w), np.imag(np.exp(1j * theta) * w), np.real(np.exp(1j * theta) * w)

def zoom(x, y, z, theta):
    return x * theta, y * theta, z * theta

# initialize hand client
hand_client = base.Client(("localhost", 11211))
hand_client.set("last_state_zoom", "initialize")
hand_client.set("last_state_rotate", "initialize")

# load dataset
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/volcano.csv")

# create figure
fig = go.Figure()

# Add surface trace
fig.add_trace(go.Surface(z=df.values.tolist(), colorscale="Viridis"))

# Update plot sizing
fig.update_layout(
    width=1000,
    height=600,
    autosize=False,
    margin=dict(t=0, b=0, l=0, r=0),
    template="plotly_white")

app = dash.Dash()

app.layout = html.Div([
    dcc.Graph(figure=fig, id='live-update-graph', 
              style={
                    "width": "80vh",
                    "height": "600px",
                    "display": "inline-block",
                    "overflow": "hidden",
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)"
                    }
                ),
    dcc.Interval(
            id='interval-component',
            interval=1*200, # in milliseconds (set a higher number if system is too loaded)
            n_intervals=0
            )
        ])

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))

def update_graph_live(n):

    camera = None

    # read the value from the .txt file saved in the OpenCV  
    info = eval(hand_client.get("update_info"))
    state = list(info)[0]
    state_value = list(info.values())[0]

    if state == "rotate_xy":
        mode = str(hand_client.get("zoom_mode")).strip("b''")
        if mode == "zoom off":
            x_eye, y_eye, z_eye = eval(hand_client.get("last_state_zoom"))

        else:
            x_eye = 1.25
            y_eye = 1.25
            z_eye = 1.25

        theta = float(state_value)
        new_x, new_y, new_z = rotate(float(x_eye), float(y_eye), float(z_eye), -theta)
        camera = dict(
                eye=dict(x=new_x, y=new_y, z=new_z)
            )

        hand_client.set("last_state_rotate", (new_x, new_y, new_z))

    if state == "zoom":
        mode = str(hand_client.get("rotation_mode")).strip("b''")
        if mode == "rotation off":
            x_eye, y_eye, z_eye = eval(hand_client.get("last_state_rotate"))

        else:
            x_eye = 1.25
            y_eye = 1.25
            z_eye = 1.25
        theta = float(state_value)
        new_x, new_y, new_z = zoom(float(x_eye), float(y_eye), float(z_eye), theta)
        camera = dict(
                eye=dict(x=new_x, y=new_y, z=new_z)
            )

        hand_client.set("last_state_zoom", (new_x, new_y, new_z))

    if camera:
        fig.update_layout(scene_camera=camera)

    return fig

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False) 

