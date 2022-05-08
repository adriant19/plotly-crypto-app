from dash import Dash

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{  # responsive for mobile viewing
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'
    }]

)

server = app.server
