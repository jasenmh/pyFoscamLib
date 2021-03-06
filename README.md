# Python API for the Foscam FI8918W.

## Two Branches
* master - depends on requests module
* vanilla - vanilla python, no dependencies, much slower

## Working
* Connect to camera by URL
* Query camera status
* Capture image from camera
* Toggle IR on/off
* Pan/tilt camera
* Set and go to preset positions
* Patrol mode
* Authenticates through digest auth

## To Do
* Finish the full api

## To Use

```python
from pyFoscamLib import CamCredentials
from pyFoscamLib import CamLoader

# create a camera profile
cr = CamCredentials("ip_addr:port", "username", "password")
CamLoader.save_camera("camera_name", cr)

# to create a camera instance
camera = CamLoader.create_camera("camera_name")

