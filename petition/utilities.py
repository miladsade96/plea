import threading


class EmailThread(threading.Thread):
    def __init__(self, email_obj):
        threading.Thread.__init__(self)
        self.email = email_obj

    def run(self):
        self.email.send()
