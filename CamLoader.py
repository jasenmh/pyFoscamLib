import os
import pickle
from FI8918W import Fi8918w


class CamLoader:
    cameras = []

    def __init__(self):
        pass

    @staticmethod
    def create_camera(name):
        if not name:
            return None

        fname = os.path.join(os.sep, os.getcwd(), "cameras", name)
        if not os.path.isfile(fname):
            return None

        # TODO: open file in binary mode?
        creds = pickle.load(open(fname, "r"))

        camera = Fi8918w(creds.url, creds.username, creds.password)
        CamLoader.cameras.append(camera)

        return camera

    @staticmethod
    def save_camera(name, creds):
        if not name or not creds:
            return False

        fname = os.path.join(os.sep, os.getcwd(), "cameras", name)
        if os.path.isfile(fname):
            return False
        # fname = "cameras/%s" % name

        # TODO: open file in binary mode?
        pickle.dump(creds, open(fname, "w"))

        return True
