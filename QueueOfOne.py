from queue import Queue, Empty, Full

class QueueOfOne():
    def __init__(self, timeoutForGet=None):
        self.queue = Queue(maxsize=1)
        self.timeoutForGet = timeoutForGet
        return
    
    def put(self, item):
        '''
        Put item into the container. Overwrite if the container is full. 
        '''
        try:
            self.queue.put_nowait(item)
        except Full:
            self.queue.get_nowait()
            self.queue.put_nowait(item)
        return

    def get(self):
        '''
        Remove and return an item from the queue. 
        Block if necessary until an item is available or until timeout is up, in which case Empty exception is raised. 
        '''
        item = self.queue.get(block=True, timeout=self.timeoutForGet)
        return item