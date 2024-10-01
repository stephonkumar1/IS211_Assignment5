#Stephon Kumar
import csv
import argparse
from queue import Queue


class Request:
    def __init__(self, timestamp, processing_time):
        self.timestamp = timestamp
        self.processing_time = processing_time

    def get_timestamp(self):
        return self.timestamp

    def get_processing_time(self):
        return self.processing_time


class Server:
    def __init__(self):
        self.current_request = None
        self.time_remaining = 0

    def tick(self):
        if self.current_request:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.current_request = None

    def busy(self):
        return self.current_request is not None

    def start_next(self, new_request):
        self.current_request = new_request
        self.time_remaining = new_request.get_processing_time()


def simulate_one_server(filename):
    server = Server()
    request_queue = Queue()
    total_wait = 0
    num_requests = 0

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamp = int(row[0])
            processing_time = int(row[2])
            request = Request(timestamp, processing_time)
            request_queue.put(request)

    current_time = 0

    while not request_queue.empty():
        current_time += 1
        if not server.busy() and not request_queue.empty():
            next_request = request_queue.get()
            wait_time = current_time - next_request.get_timestamp()
            total_wait += wait_time
            num_requests += 1
            server.start_next(next_request)

        server.tick()

    average_wait = total_wait / num_requests if num_requests > 0 else 0
    print(f"Average Wait Time with One Server: {average_wait:.2f} seconds")
    return average_wait


def simulate_many_servers(filename, num_servers):
    servers = [Server() for _ in range(num_servers)]
    queues = [Queue() for _ in range(num_servers)]
    total_wait = 0
    num_requests = 0
    round_robin_counter = 0

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamp = int(row[0])
            processing_time = int(row[2])
            request = Request(timestamp, processing_time)
            queues[round_robin_counter % num_servers].put(request)
            round_robin_counter += 1

    current_time = 0
    while any(not q.empty() for q in queues):
        current_time += 1
        for i in range(num_servers):
            server = servers[i]
            if not server.busy() and not queues[i].empty():
                next_request = queues[i].get()
                wait_time = current_time - next_request.get_timestamp()
                total_wait += wait_time
                num_requests += 1
                server.start_next(next_request)

            server.tick()

    average_wait = total_wait / num_requests if num_requests > 0 else 0
    print(f"Average Wait Time with {num_servers} Servers: {average_wait:.2f} seconds")
    return average_wait


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Request Simulator")
    parser.add_argument("--file", required=True, help="Input CSV file containing requests")
    parser.add_argument("--servers", type=int, help="Number of servers (default is 1)", default=1)
    args = parser.parse_args()

    if args.servers == 1:
        simulate_one_server(args.file)
    else:
        simulate_many_servers(args.file, args.servers)
