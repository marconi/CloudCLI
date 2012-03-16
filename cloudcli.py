# -*- coding: utf-8 -*-

#####################################################
## Cloud CLI is a basic Dropbox client that lets you:
## upload, download, move and list files.
##
## Requirements: cmd2, Dropbox Python SDK
######################################################


import os
import pickle
from cmd2 import Cmd
from dropbox import client, rest, session


APP_KEY = ''
APP_SECRET = ''
ACCESS_TYPE = 'dropbox'

ROOT = os.path.abspath(os.path.dirname(__file__))
ACCESS_TOKEN = os.path.join(ROOT, 'access_token')

class CloudCli(object):
    def __init__(self):
        self.sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        self.request_token = self.sess.obtain_request_token()

        if not os.path.exists(ACCESS_TOKEN):
            self.authorize()

        handle = open(ACCESS_TOKEN, 'r')
        self.access_token = pickle.loads(handle.read())
        handle.close()

        self.sess.set_token(self.access_token.key, self.access_token.secret)
        self.client = client.DropboxClient(self.sess)

    def authorize(self):
        url = self.sess.build_authorize_url(self.request_token)
        print "URL: %s" % url
        print "Please visit the URL and press the 'Allow'" \
              "button, then hit 'Enter' here."
        raw_input()

        self.access_token = self.sess.obtain_access_token(self.request_token)
        handle = open(ACCESS_TOKEN, 'wb')
        handle.write(pickle.dumps(self.access_token))
        handle.close()

    def upload(self, filename, location):
        filename = os.path.normpath(os.path.expanduser(filename))
        location = os.path.join(location, os.path.basename(filename))
        try:
            return self.client.put_file(location, open(filename, 'r'))
        except rest.ErrorResponse, e:
            print e

    def download(self, filename, destination):
        try:
            remote_handle = self.client.get_file(filename)
            local_filename = os.path.join(
                os.path.normpath(os.path.expanduser(destination)),
                os.path.basename(filename))
            local_handle = open(local_filename, 'wb')
            local_handle.write(remote_handle.read())
            remote_handle.close()
            local_handle.close()
        except rest.ErrorResponse, e:
            print e

    def move(self, from_path, to_path):
        try:
            self.client.file_move(from_path, to_path)
        except rest.ErrorResponse, e:
            print e

    def list(self, remote_path):
        try:
            metadata = self.client.metadata(remote_path)
            files = metadata.get('contents', None)
            if not files:
                print files
            print "\n".join([filemeta['path'] for filemeta in files])
        except rest.ErrorResponse, e:
            print e


class CloudCliCmd(Cmd, object):

    def __init__(self):
        super(CloudCliCmd, self).__init__()
        self.cloudcli = CloudCli()
        self.prompt = "Cloud >>> "

    def do_put(self, arg):
        filename, upload_path = arg.split()
        self.cloudcli.upload(filename, upload_path)

    def do_get(self, arg):
        tmp = arg.split()
        if len(tmp) > 1:
            filename, download_path = tmp
        else:
            download_path = ""
            filename = tmp[0]
        self.cloudcli.download(filename, download_path)

    def do_mv(self, arg):
        from_path, to_path = arg.split()
        self.cloudcli.move(from_path, to_path)

    def do_ls(self, arg):
        self.cloudcli.list(arg)

    def do_EOF(self, line):
        return True


if __name__ == "__main__":
    CloudCliCmd().cmdloop()
