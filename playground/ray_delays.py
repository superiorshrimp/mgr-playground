import ray
import asyncio
from time import time, sleep

@ray.remote
class AgentRemote:
    def __init__(self):
        self.value = 0
        self.data = []

    def main_loop(self):
        for i in range(20):
            sleep(2)
            print("R", self.value)
            self.value += 1

    def get_value(self):
        return (self.value, time())

    def receive(self, data):
        self.data.append(data)

@ray.remote
class AgentLocal:
    def __init__(self, remote_agent):
        self.value = None
        self.timestamp = time()
        self.result = []
        self.remote_agent = remote_agent

    def main_loop(self):
        for i in range(10):
            sleep(1)
            print("L", self.value, self.result)
            self.get_value_from_remote()
            self.set_value_from_remote()

    def get_value_from_remote(self):
        self.result.append(self.remote_agent.get_value.remote())

    def set_value_from_remote(self):
        received = ray.wait(self.result, timeout=None)[0]
        if received[0]:
            result = ray.get(received[0])
            print(result)
            if result[1] > self.timestamp:
                print("yes")
                self.value = result[0]
                self.timestamp = result[1]
            else: print("no")

def main():
    a_remote = AgentRemote.remote()
    a_local = AgentLocal.remote(a_remote)

    r_ref = a_remote.main_loop.remote()
    l_ref = a_local.main_loop.remote()
    ray.get([r_ref, l_ref])

if __name__ == '__main__':
    ray.init()
    main()