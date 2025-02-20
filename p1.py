import socket

def start_server(host='127.0.0.1', port=65432):
    # 创建一个TCP/IP套接字
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定套接字到指定的地址和端口
        server_socket.bind((host, port))
        # 监听传入的连接
        server_socket.listen()
        print(f"服务器正在 {host}:{port} 上监听...")

        while True:
            # 等待连接
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"已连接到 {client_address}")
                while True:
                    # 接收数据
                    data = client_socket.recv(1024)
                    if not data:
                        # 如果没有数据，关闭连接
                        print(f"与 {client_address} 的连接已关闭")
                        break
                    # 发送数据回客户端
                    client_socket.sendall(data)

if __name__ == "__main__":
    start_server()