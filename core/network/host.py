"""
Servidor do modo cooperativo em LAN: quem "hospeda" a partida roda esta
classe, que aceita conexões de outros jogadores, recebe o input de cada
um continuamente (em threads separadas) e transmite o estado do mundo
(snapshot) simulado pelo host a cada quadro. A simulação em si continua
rodando normalmente no loop principal do jogo, no processo do host.
"""

import socket
import threading

from core.network.protocol import DEFAULT_PORT, send_json, recv_json


class GameServer:
    """Aceita conexões de clientes na rede local e faz a ponte entre o
    input de cada um e o loop principal do jogo."""

    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self._listen_socket = None
        self._client_sockets = {}     # client_id -> socket
        self._latest_inputs = {}      # client_id -> dict de input mais recente
        self._lock = threading.Lock()
        self._next_client_id = 1
        self._running = False

    def local_ip(self):
        """Descobre o IP da máquina na rede local (para exibir na tela
        de hospedagem). Não chega a enviar dados de verdade — só usa o
        truque de abrir um socket UDP "conectado" a um endereço externo
        para o sistema operacional escolher a interface de rede certa."""
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))
            ip = probe.getsockname()[0]
            probe.close()
            return ip
        except OSError:
            return socket.gethostbyname(socket.gethostname())

    def start(self):
        """Abre o socket de escuta e começa a aceitar conexões em uma
        thread separada, sem bloquear o loop principal do jogo."""
        self._listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_socket.bind(("0.0.0.0", self.port))
        self._listen_socket.listen()
        self._running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while self._running:
            try:
                client_sock, _addr = self._listen_socket.accept()
            except OSError:
                break

            with self._lock:
                client_id = f"client-{self._next_client_id}"
                self._next_client_id += 1
                self._client_sockets[client_id] = client_sock
                self._latest_inputs[client_id] = {}

            try:
                # Avisa o cliente qual id ele recebeu, para que ele saiba
                # se reconhecer dentro dos snapshots recebidos depois.
                send_json(client_sock, {"you_are": client_id})
            except OSError:
                self._disconnect(client_id)
                continue

            threading.Thread(target=self._read_loop, args=(client_id, client_sock), daemon=True).start()

    def _read_loop(self, client_id, client_sock):
        """Fica lendo o input desse cliente continuamente, sempre
        guardando apenas o mais recente — mensagens antigas não importam
        mais assim que uma nova chega."""
        try:
            while self._running:
                input_data = recv_json(client_sock)
                with self._lock:
                    self._latest_inputs[client_id] = input_data
        except (ConnectionError, OSError, ValueError):
            pass
        finally:
            self._disconnect(client_id)

    def _disconnect(self, client_id):
        with self._lock:
            sock = self._client_sockets.pop(client_id, None)
            self._latest_inputs.pop(client_id, None)
        if sock:
            try:
                sock.close()
            except OSError:
                pass

    def connected_client_ids(self):
        """Lista os ids dos clientes atualmente conectados."""
        with self._lock:
            return list(self._client_sockets.keys())

    def get_inputs(self):
        """Retorna uma cópia do último input recebido de cada cliente
        conectado (dict client_id -> input)."""
        with self._lock:
            return dict(self._latest_inputs)

    def broadcast_snapshot(self, snapshot):
        """Envia o snapshot do mundo simulado para todos os clientes
        conectados. Remove silenciosamente quem já desconectou."""
        with self._lock:
            client_items = list(self._client_sockets.items())
        for client_id, sock in client_items:
            try:
                send_json(sock, snapshot)
            except (ConnectionError, OSError):
                self._disconnect(client_id)

    def stop(self):
        """Encerra o servidor: para de aceitar conexões e fecha todos os
        sockets abertos (clientes e o socket de escuta)."""
        self._running = False
        with self._lock:
            sockets = list(self._client_sockets.values())
            self._client_sockets.clear()
            self._latest_inputs.clear()
        for sock in sockets:
            try:
                sock.close()
            except OSError:
                pass
        if self._listen_socket:
            try:
                self._listen_socket.close()
            except OSError:
                pass
