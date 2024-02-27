import time
from queue import Queue


class MockedStreamer:
    def __init__(self):
        self.queue = Queue()
        self.done = False

    def put(self, value):
        self.queue.put(value)

    def __iter__(self):
        return self

    def __next__(self):
        while self.queue.empty() and not self.done:
            time.sleep(1)

        if not self.queue.empty():
            return self.queue.get()

        if self.done:
            raise StopIteration

    def mark_done(self):
        self.done = True


class MockedMessage:
    def __init__(self, id, prompt, config, chatbot):
        self.streamer = MockedStreamer()

    def converse(self):
        time.sleep(5)
        for letter in ["H", "E", "L", "L", "O", " ", "W", "O", "R", "L", "D"]:
            print(f"Puuting letter: {letter}")
            self.streamer.put(letter)
            time.sleep(1)
        self.streamer.mark_done()
        print("Done streaming response")

        return {"id": "1234", "response": "Hello World"}
