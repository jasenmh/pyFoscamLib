import urllib2


class fi8918w:
    """
    This class can be used to send commands to a Foscam FI8918W IP camera.
    """

    def __init__(self, url="", username="", password=""):
        self.url = url
        self.username = username
        self.password = password
        self.camera_id = ""
        self.camera_name = ""
        self.alarm_status = ""

    # ---------- Private methods ----------
    def _query_camera(self, command, arg=None):
        if self.username == "" or self.password == "":
            return -1

        if self.url == "":
            return -1

        nurl = "http://" + self.url + "/" + command
        nurl += "?user=" + self.username + "&pwd=" + self.password
        if arg is not None:
            nurl = nurl + "&" + arg

        r = urllib2.urlopen(nurl)
        resp = r.readlines()
        #resp = r.read()

        return resp

    def _query_camera_binary(self, command, arg='picture', ext='jpg'):
        if self.username == "" or self.password == "":
            return -1

        if self.url == "":
            return -1

        nurl = "http://" + self.url + "/" + command
        nurl += "?user=" + self.username + "&pwd=" + self.password
        nurl += "&next_url=" + arg

        fname = arg + '.' + ext

        b = urllib2.urlopen(nurl)
        fout = open(fname, 'wb')
        fout.write(b.read())
        fout.close()

        return fname

    # ---------- Public methods ----------
    def getStatus(self):
        resp = self._query_camera('get_status.cgi')

        if resp == -1:
            status = -1
        else:
            status = {}
            for line in resp:
                line = line[4:]  # strip "var "
                line = line.rstrip(';\n')
                parts = line.split('=')
                if len(parts) > 1:
                    if parts[1].rfind("'") == -1:
                        status[parts[0]] = parts[1]
                    else:
                        status[parts[0]] = parts[1].replace("'", "")

                if parts[0] == 'alarm_status':
                    self.alarm_status = status['alarm_status']
                elif parts[0] == 'id':
                    self.camera_id = status['id']
                elif parts[0] == 'alias':
                    self.camera_name = status['alias']

        return status

    def setMotionAlarm(self, alarmOn):
        if alarmOn:
            arg = "motion_armed=1"
        else:
            arg = "motion_armed=0"

        resp = self._query_camera('set_alarm.cgi', arg)

        if resp == -1:
            return -1
        else:
            return 1

    def getSnapshot(self, fname='picture'):
        status = self._query_camera_binary('snapshot.cgi', fname)

        return status


if __name__ == "__main__":
    print("pyFoscam: import this module to use it")
