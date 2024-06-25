class AudioQueue:
    def __init__(self) :
        self.queue = []

    def add(self, audio):
        self.queue.append(audio)

    def get_next_audio(self):
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def skip_audio(self):
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def remove_audio(self,index):
        if 0 <= index<len(self.queue):
            self.queue.pop(index)
        return None
    def view_queue(self):
        return self.queue

    def clean_queue(self):
        self.queue.clear()
