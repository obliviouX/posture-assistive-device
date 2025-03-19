# posture-assistive-device
Senior design project

Right Wrist, Left Wrist, and Neck all communicate to the Display using Bluetooth Low Energy.

To create an executable for the data logger, run:
`pip3 install pyinstaller`, then
`pyinstaller --onefile posture-assistive-device-data-logger.py`, which will create the executable in the `dist` folder. The data file is created wherever the executable is ran.
