import re
import requests
from requests.auth import HTTPDigestAuth

DEBUG = False


class Fi8918w:
    """
    This class can be used to send commands to a Foscam FI8918W IP camera.
    """

    # TODO: replace individual cred pieces with CamCredentials class
    def __init__(self, url="", username="", password="", realm=None):
        self.camera_url = "http://" + url + "/"
        self.username = username
        self.password = password
        self.realm = realm
        self.camera_id = ""
        self.camera_name = ""
        self.alarm_status = ""
        self.auth = None

    # ---------- Private methods ----------
    def _make_request(self, url):
        if not self.auth:
            self.auth = HTTPDigestAuth(self.username, self.password)

        resp = requests.get(url, auth=self.auth)

        return resp

    def _query_camera(self, command):
        """ This method sends requests/commands to the camera when the return does not need to be saved to a binary
        file.
        :param command: cgi request/command to the camera
        :return: returns the urllib2.urlopen return value
        """
        if not self.camera_url or not command:
            return None

        resp = self._make_request(self.camera_url + command)

        if resp:
            return resp
        else:
            return None

    def _query_camera_binary(self, command):
        """
        This method sends requests/commands to the camera when the return does need to be saved to a binary file.
        Used for saving snapshots from the camera for example.
        :param command: cgi request/command to the camera
        :return: data stream
        """
        if not self.camera_url or not command:
            return None

        b = self._make_request(self.camera_url + command)

        if b:
            return b.content
        else:
            return None

    def _cam_pzt_step(self, command, degrees):
        if degrees < 1:
            # invalid movement amount makes the camera do funny things
            return None
        return self._query_camera('decoder_control.cgi?command={0}&onestep=1&degree={1}'.format(command, degrees))

    # ---------- Public methods ----------
    def get_status(self):
        resp = self._query_camera('get_params.cgi')

        if resp is None:
            status = None
        else:
            status = {}
            for line in resp.text.split("\n"):
                m = re.search("var ([\w.]+)='*([\w.-]+)'*", line)
                if m:
                    status[m.group(1)] = m.group(2)
                else:
                    if DEBUG:
                        print "failed parsing %s" % line

            self.camera_id = status['id']
            self.camera_name = status['alias']

        return status

    def set_motion_alarm(self, alarm):
        """ This method enables and disables the camera alarming on motion.
        :param alarm: True - enable alarm, False - disable alarm
        :return: True on success, False otherwise
        """
        if alarm:
            arg = "motion_armed=1"
        else:
            arg = "motion_armed=0"

        resp = self._query_camera('set_alarm.cgi?%s' % arg)

        return False if not resp else True

    def get_snapshot(self, fname=None):
        """ This method gets a snapshot from the camera and returns the image string.  If a filename is specified it
        writes out to the file too
        :param fname: optional, name of an image file to which the data will be written
        :return: returns the image string
        """
        img_str = self._query_camera_binary('snapshot.cgi')
        if fname:
            with open(fname, 'wb') as fout:
                fout.write(img_str)
        return img_str

    def ir_on(self):
        """ This method sends command 95 to the camera which turns on the infrared emitters
        :return: returns the url2lib response from the camera
        """
        resp = self._query_camera('decoder_control.cgi?command=95')
        return resp

    def ir_off(self):
        """ This method sends command 94 to the camera which turns off the infrared emitters
        :return: returns the url2lib response from the camera
        """
        return self._query_camera('decoder_control.cgi?command=94')

    def cam_center(self):
        """ This method sends command 25 to the camera which runs a set of movements that centers the camera
        :return: returns the url2lib response from the camera
        """
        resp = self._query_camera('decoder_control.cgi?command=25')
        return resp

    def cam_step_up(self, degrees=1):
        """ Send command 0 (up) to the decoder_control.cgi to make the camera move up
        :param degrees: degrees of the desired move
        :return: None on invalid commands or move amount
        """
        return self._cam_pzt_step(command=0, degrees=degrees)

    def cam_step_down(self, degrees=1):
        """ Send command 2 (down) to the decoder_control.cgi to make the camera move down
        :param degrees: degrees of the desired move
        :return: None on invalid commands or move amount
        """
        return self._cam_pzt_step(command=2, degrees=degrees)

    def cam_step_left(self, degrees=1):
        """ Send command 6 (left) to the decoder_control.cgi to make the camera move left.  Note this is opposite of the
        camera documentation.  This was tested with camera on desk.
        :param degrees: degrees of the desired move
        :return: None on invalid commands or move amount
        """
        return self._cam_pzt_step(command=6, degrees=degrees)

    def cam_step_right(self, degrees=1):
        """ Send command 4 (right) to the decoder_control.cgi to make the camera move right.  Note this is opposite of
        the camera documentation.  This was tested with camera on desk.
        :param degrees: degrees of the desired move
        :return: None on invalid commands or move amount
        """
        return self._cam_pzt_step(command=4, degrees=degrees)

    def start_patrol(self, vert=False, horiz=False):
        """
        :param vert: Setting to True enables veritcal patrol mode
        :param horiz: Setting to True enables horizontal patrol mode
        """
        if vert:
            self._query_camera('decoder_control.cgi?command=26')
        if horiz:
            self._query_camera('decoder_control.cgi?command=28')

    def stop_patrol(self, vert=False, horiz=False):
        """
        :param vert: Setting to True stops veritcal patrol mode
        :param horiz: Setting to True stops horizontal patrol mode
        """
        if vert:
            self._query_camera('decoder_control.cgi?command=27')
        if horiz:
            self._query_camera('decoder_control.cgi?command=29')

    def set_preset(self, preset_num=1):
        """ Sets the non-volatile preset indicated to the current PZT position
        :param preset_num: location 1-8 for presets
        :return: None on failure otherwise the urllib2 response
        """
        if 0 > preset_num > 8:
            # Invalid preset #
            return None
            # commands 30..45 alternate set preset #, goto preset# starting at command 30
        command = (preset_num * 2 - 2) + 30
        self._query_camera('decoder_control.cgi?command={0}'.format(command))

    def goto_preset(self, preset_num=1):
        """ Moves the PZT to the non-volatile preset indicated
        :param preset_num: location 1-8 for presets
        :return: None on failure otherwise the urllib2 response
        """
        if 0 > preset_num > 8:
            # Invalid preset #
            return None
        # commands 30..45 alternate set preset #, goto preset# starting at command 30
        command = (preset_num * 2 - 1) + 30
        self._query_camera('decoder_control.cgi?command={0}'.format(command))


if __name__ == "__main__":
    print("pyFoscam: import this module to use it")
