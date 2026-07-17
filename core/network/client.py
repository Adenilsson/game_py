"""
Cliente do modo cooperativo em LAN: quem "entra" na partida de outra
pessoa roda esta classe, que conecta no host, manda o input local a
cada quadro e recebe o snapshot do mundo simulado pelo host para
desenhar (o cliente não roda nenhuma simulação própria).
"""

import socket
import threading

from core.network.protocol import send_json, recv_json


class GameClient:
    """Conecta a um host na rede local, envia o input do jogador local
    continuamente e mantém o snapshot mais recente recebido do host."""

    def __init__(self):
        self._sock = None
        self._latest_snapshot = None
        self._lock = threading.Lock()
        self._running = False
        self.player_id = None
        self.connection_error = None

    def connect(self, host_ip, port, timeout=5):
        """Conecta no host informado e lê a mensagem de boas-vindas com
        o id atribuído a este cliente. Levanta OSError se a conexão
        falhar (host fora do ar, IP errado, firewall bloqueando, etc.)."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host_ip, port))
        welcome = recv_json(sock)
        self.player_id = welcome.get("you_are")
        sock.settimeout(None)

        self._sock = sock
        self._running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        """Fica lendo snapshots do host continuamente, sempre guardando
        apenas o mais recente."""
        try:
            while self._running:
                snapshot = recv_json(self._sock)
                with self._lock:
                    self._latest_snapshot = snapshot
        except (ConnectionError, OSError, ValueError) as exc:
            self.connection_error = str(exc)
        finally:
            self._running = False

    def send_input(self, input_data):
        """Manda o input local (teclas pressionadas) para o host. Ignora
        silenciosamente falhas de envio — a thread de leitura já detecta
        e sinaliza a queda da conexão em `connection_error`."""
        if not self._sock:
            return
        try:
            send_json(self._sock, input_data)
        except OSError:
            pass

    def get_latest_snapshot(self):
        """Retorna o snapshot mais recente recebido do host, ou None se
        ainda não chegou nenhum."""
        with self._lock:
            return self._latest_snapshot

    def is_connected(self):
        """Indica se a conexão com o host ainda está ativa."""
        return self._running and self.connection_error is None

    def disconnect(self):
        """Encerra a conexão com o host."""
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
