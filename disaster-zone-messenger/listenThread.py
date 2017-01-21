from threading import Thread

class ListenThread(Thread):
    def __init__(self, router):
        self.router = router;
        Thread.__init__(self)
        self.daemon = True
        self.start()
    
    def run(self):
        self.router.listen()