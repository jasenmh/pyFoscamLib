import os
import pickle
from FI8918W import Fi8918w as Foscam
from AuthHandlerHelper import CamCredentials


class CamLoader:
    cameras = []

    def __init__(self):
        # CamLoader.cameras = []
        pass

    @staticmethod
    def create_camera(name):
        if not name:
            return None

        fname = os.path.join(os.sep, os.getcwd(), "cameras", name)

        if not os.path.isfile(fname):
            return None

        creds = pickle.load(open(fname, "r"))

        camera = Foscam(creds.url, creds.username, creds.password)
        CamLoader.cameras.append(camera)

        return camera

    @staticmethod
    def save_camera(name, creds):
        fname = os.path.join(os.sep, os.getcwd(), "cameras", name)

        if os.path.isfile(fname):
            return None

        pickle.dump(creds, open(fname, "w"))

        return True
