import urllib
import urllib2

"""
This module facilitates the use of a Foscam FI8918W IP Camera. It may work
with other Foscam (or any other) cameras that have the same API.
"""

class FoscamCamera:

  """
  This class can be used to send commands to a Foscam IP camera.
  """

  def __init__(self):
    self.ipAddress = ""
    self.userName = ""
    self.passWord = ""
    self.cameraName = ""


