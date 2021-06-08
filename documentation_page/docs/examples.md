# Welcome to H.G.I.2



## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    run.py				   # The script that runs all other needed scripts
    HandTrackingModule.py	# The script that detects the hands with googles mediapipe
    hand_gesture.py			# The script that uses the detected hands, detects hand gestures and saves values to change the camera scene.
    control_dash_app.py    # The script that uses the saved zoom and rotation values and translates these values into changes in the layout of the plotly dash figure.
    
