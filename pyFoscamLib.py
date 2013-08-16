import urllib
import urllib2

"""
This module facilitates the use of a Foscam FI8918W IP Camera. It may work
with other Foscam (or any other) cameras that have the same API.
"""

class camera:

  """
  This class can be used to send commands to a Foscam IP camera.
  """

  def __init__(self):
    self.url = ""
    self.userName = ""
    self.passWord = ""
    self.cameraId = ""
    self.cameraName = ""

  def queryCamera(self, command):
    if self.url == "":
      return -1;

    nurl = "http://" + self.url + "/" + command

    r = urllib2.urlopen(nurl)
    resp = r.readlines()
 
    return resp

  def queryCameraSecure(self, command):
    if self.url == "":
      return -1;

    nurl = "http://" + self.url + "/" + command
    print nurl;
    if self.userName != "" and self.passWord != "":
      nurl += "?user=" + self.userName + "&pwd=" + self.passWord

    r = urllib2.urlopen(nurl)
    resp = r.readlines()
 
    return resp

  def getStatus(self):
    resp = self.queryCamera('get_status.cgi')

    if resp == -1:
      status = -1
    else:
      status = {}
      for line in resp:
        # line = line.lstrip('var ')
        line = line[4:] # strip "var "
        line = line.rstrip(';\n')
        parts = line.split('=')
        if parts[1].rfind("'") == -1:
          status[parts[0]] = int(parts[1])
        else:
          status[parts[0]] = parts[1].replace("'", "")

    return status

  def connect(self, uname = None, pword = None):
    status = self.getStatus()

    if status == -1:
      return -1

    self.cameraId = status['id']
    self.cameraName = status['alias']

    return 1
