import urllib
import urllib2

"""
This module facilitates the use of a Foscam FI8918W IP Camera. It may work
with other Foscam (or any other) cameras that have the same API.
"""

class fi8918w:

  """
  This class can be used to send commands to a Foscam IP camera.
  """

  def __init__(self, url="", userName="", passWord=""):
    self.url = url
    self.userName = userName
    self.passWord = passWord
    self.cameraId = ""
    self.cameraName = ""
    self.alarmStatus = ""

  # ---------- Private methods ----------
  def __queryCamera(self, command, arg = None):
    if self.userName == "" or self.passWord == "":
      return -1

    if self.url == "":
      return -1;

    nurl = "http://" + self.url + "/" + command
    nurl += "?user=" + self.userName + "&pwd=" + self.passWord
    if arg != None:
      nurl = nurl + "&" + arg

    r = urllib2.urlopen(nurl)
    resp = r.readlines()
    #resp = r.read()
 
    return resp

  def __queryCameraBinary(self, command, arg = 'picture', ext = 'jpg'):
    if self.userName == "" or self.passWord == "":
      return -1

    if self.url == "":
      return -1

    nurl = "http://" + self.url + "/" + command
    nurl += "?user=" + self.userName + "&pwd=" + self.passWord
    nurl += "&next_url=" + arg

    fname = arg + '.' + ext

    b = urllib2.urlopen(nurl)
    fout = open(fname, 'wb')
    fout.write(b.read())
    fout.close()

    return fname

  # ---------- Public methods ----------
  def getStatus(self):
    resp = self.__queryCamera('get_status.cgi')

    if resp == -1:
      status = -1
    else:
      status = {}
      for line in resp:
        line = line[4:] # strip "var "
        line = line.rstrip(';\n')
        parts = line.split('=')
        if len(parts) > 1:
          if parts[1].rfind("'") == -1:
            status[parts[0]] = parts[1]
          else:
            status[parts[0]] = parts[1].replace("'", "")

        if parts[0] == 'alarm_status':
          self.alarmStatus = status['alarm_status']
        elif parts[0] == 'id':
          self.cameraId = status['id']
        elif parts[0] == 'alias':
          self.cameraName = status['alias']

    return status

  def setMotionAlarm(self, alarmOn):
    if alarmOn == True:
      arg = "motion_armed=1"
    else:
      arg = "motion_armed=0"

    resp = self.__queryCamera('set_alarm.cgi', arg)

    if resp == -1:
      return -1
    else:
      return 1

  def getSnapshot(self, fname='picture'):
    status = self.__queryCameraBinary('snapshot.cgi', fname)

    return status


if __name__ == "__main__":
  print("pyFoscam: import this module to use it")
