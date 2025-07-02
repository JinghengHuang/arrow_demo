from websockets.sync.client import connect

def hello():
    uri = "ws://localhost:8080"
    with connect(uri) as websocket:
        name = "Jingheng"
        websocket.send(name)
        print(f">>> {name}")

        greeting = websocket.recv()
        print(f"<<< {greeting}")

if __name__ == "__main__":
    hello()