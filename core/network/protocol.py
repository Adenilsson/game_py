"""
Framing e serialização das mensagens trocadas entre host e cliente no
modo cooperativo em LAN: cada mensagem é um objeto JSON prefixado por um
cabeçalho de 4 bytes (tamanho, big-endian), para que o receptor saiba
exatamente onde uma mensagem termina e a próxima começa dentro do fluxo
contínuo de bytes do TCP.
"""

import json
import struct

HEADER_SIZE = 4
DEFAULT_PORT = 5555


def send_json(sock, obj):
    """Serializa `obj` em JSON e envia com um cabeçalho de tamanho na
    frente, para que `recv_json` do outro lado saiba quantos bytes ler."""
    data = json.dumps(obj).encode("utf-8")
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)


def _recv_exact(sock, n):
    """Lê exatamente `n` bytes do socket. Levanta ConnectionError se a
    conexão fechar antes de completar a leitura."""
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Conexão encerrada pelo outro lado")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_json(sock):
    """Lê uma mensagem JSON completa do socket (bloqueante), seguindo o
    framing de `send_json`. Levanta ConnectionError/ValueError se a
    conexão cair ou os dados recebidos forem inválidos."""
    header = _recv_exact(sock, HEADER_SIZE)
    (length,) = struct.unpack(">I", header)
    data = _recv_exact(sock, length)
    return json.loads(data.decode("utf-8"))
