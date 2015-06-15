import urllib2
import base64

DEBUG = True


class PreemptiveDigestAuthHandler(urllib2.HTTPDigestAuthHandler):
    """
    This class is based on @thom_nic's reply to
    http://stackoverflow.com/questions/4628610/does-urllib2-support-preemptive-authentication-authentication
    and digest auth code by PockyBum522 and crew at FamiLab.
    """

    def __init__(self, password_mgr=None):
        if password_mgr is None:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        #super(PreemptiveDigestAuthHandler, self).__init__(password_mgr)
        urllib2.HTTPDigestAuthHandler.__init__(self, password_mgr)
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password

    def http_request(self, req):

        uri = req.get_full_url()
        user, pw = self.passwd.find_user_password(None, uri)

        if pw is None:
            return req

        raw = "%s:%s" % (user, pw)
        auth = 'Digest %s' % base64.b64encode(raw).strip()
        req.add_unredirected_header('Authorization', auth)

        return req


class CamCredentials:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
