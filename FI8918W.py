import urllib2
import re
import base64
import sys
import os


class fi8918w:
    """
    This class can be used to send commands to a Foscam FI8918W IP camera.
    """

    def __init__(self, url="", username="", password=""):
        self.camera_url = url
        self.username = username
        self.password = password
        self.camera_id = ""
        self.camera_name = ""
        self.alarm_status = ""
        self.authheader = None

    # ---------- Private methods ----------
    def _basic_auth(self, url):
        """ This method takes the requested URL, check if basic authentication is required and sets up the HTTP GET with the
        base64 authentication.  Used http://www.voidspace.org.uk/python/articles/authentication.shtml as a guide for doing this
        :param url: url to be requested from IP camera
        :return: returns the urllib2.urlopen return value
        """
        if not self.username or not self.password or not url:
            # invalid request
            return -1
        # Make a request
        req = urllib2.Request(url)
        # If we haven't set up authentication yet, try to cache it
        if not self.authheader:
            # Encode the basic authentication into a base64 string
            try:
                handle = urllib2.urlopen(req)
            except IOError, e:
                # Here we want to fail if there's authentication required on this page and we'll continue
                pass
            else:
                # This page is not protected by authentication
                return handle
            # Extract the scheme and realm in using reg-ex
            authline = e.headers['www-authenticate']
            authobj = re.compile(r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''', re.IGNORECASE)
            matchobj = authobj.match(authline)
            scheme = matchobj.group(1)
            _ = matchobj.group(2)   # un-used.  This would be the realm, left here for completeness
            if scheme.lower() != 'basic':
                print "Basic authentication failed for some reason"
                sys.exit(1)
            base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
            self.authheader = "Basic %s" % base64string

        # Add the authentication header
        req.add_header("Authorization", self.authheader)
        return urllib2.urlopen(req)

    def _query_camera(self, command):
        """ This method sends requests/commands to the camera when the return does not need to be saved to a binary file.
        :param command: cgi request/command to the camera
        :return: returns the urllib2.urlopen return value
        """
        if not self.camera_url or not command:
            return -1
        nurl = "http://" + self.camera_url + "/" + command
        # Set up the basic authentication, and get the data
        return self._basic_auth(nurl)

    def _query_camera_binary(self, command):
        """
        This method sends requests/commands to the camera when the return does need to be saved to a binary file.
        Used for saving snapshots from the camera for example.
        :param command: cgi request/command to the camera
        :param arg: base pathname and file name without extension where the picture will be saved
        :return: pathname and filename of the output file
        """
        if not self.camera_url or not command:
            return -1
        nurl = "http://" + self.camera_url + "/" + command
        b = self._basic_auth(nurl)
        return b.read()

    def _cam_pzt_step(self, command, degrees):
        if degrees < 1:
            # invalid movement amount makes the camera do funny things
            return -1
        return self._query_camera('decoder_control.cgi?command={0}&onestep=1&degree={1}'.format(command, degrees))

    # ---------- Public methods ----------
    def get_status(self):
        resp = self._query_camera('get_params.cgi')

        if resp == -1:
            status = -1
        else:
            status = {}
            for line in resp:
                line = line[4:]  # strip "var "
                line = line.rstrip(';\n')
                parts = line.split('=')
                if len(parts) > 1:
                    status[parts[0]] = parts[1].replace("'", "")

            self.camera_id = status['id']
            self.camera_name = status['alias']

        return status

    def set_motion_alarm(self, alarm):
        if alarm:
            arg = "motion_armed=1"
        else:
            arg = "motion_armed=0"

        resp = self._query_camera('set_alarm.cgi', arg)

        return -1 if resp == -1 else 1

    def get_snapshot(self, fname=None):
        """ This method gets a snapshot from the camera and returns the image string.  If a filename is specified it writes
        out to the file too
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

    def cam_step_up(self, degrees=1):
        """ Send command 0 (up) to the decoder_control.cgi to make the camera move up
        :param degrees: degrees of the desired move
        :return: -1 on invalid commands or move amount
        """
        return self._cam_pzt_step(command=0, degrees=degrees)

    def cam_step_down(self, degrees=1):
        """ Send command 2 (down) to the decoder_control.cgi to make the camera move down
        :param degrees: degrees of the desired move
        :return: -1 on invalid commands or move amount
        """
        return self._cam_pzt_step(command=2, degrees=degrees)

    def cam_step_left(self, degrees=1):
        """ Send command 6 (left) to the decoder_control.cgi to make the camera move left.  Note this is opposite of the
        camera documentation.  This was tested with camera on desk.
        :param degrees: degrees of the desired move
        :return: -1 on invalid commands or move amount
        """
        return self._cam_pzt_step(command=6, degrees=degrees)

    def cam_step_right(self, degrees=1):
        """ Send command 4 (right) to the decoder_control.cgi to make the camera move right.  Note this is opposite of the
        camera documentation.  This was tested with camera on desk.
        :param degrees: degrees of the desired move
        :return: -1 on invalid commands or move amount
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
        :return: -1 on failure otherwise the urllib2 response
        """
        if 0 > preset_num > 8:
            # Invalid preset #
            return -1
            # commands 30..45 alternate set preset #, goto preset# starting at command 30
        command = (preset_num * 2 - 2) + 30
        self._query_camera('decoder_control.cgi?command={0}'.format(command))

    def goto_preset(self, preset_num=1):
        """ Moves the PZT to the non-volatile preset indicated
        :param preset_num: location 1-8 for presets
        :return: -1 on failure otherwise the urllib2 response
        """
        if 0 > preset_num > 8:
            # Invalid preset #
            return -1
        # commands 30..45 alternate set preset #, goto preset# starting at command 30
        command = (preset_num * 2 - 1) + 30
        self._query_camera('decoder_control.cgi?command={0}'.format(command))


if __name__ == "__main__":
    print("pyFoscam: import this module to use it")
