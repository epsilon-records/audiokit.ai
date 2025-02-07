from concurrent import futures
import grpc
import time

# Import your generated gRPC modules here
# from . import audio_pb2_grpc, audio_pb2

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Register your gRPC servicers here.
    # audio_pb2_grpc.add_AudioServiceServicer_to_server(AudioServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)  # Run forever
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve() 