# /lib/api_queue.py

import urequests
import ujson
import time
from collections import deque

SERVER_IP  = "10.253.41.219"
LOG_URL   = f"http://{SERVER_IP}/access/log.php"

# Buffer en RAM para hasta 200 eventos no enviados
pendientes = deque([], 200)    # primero la lista, luego el maxlen

def _intenta_enviar(evento):
    """
    Intenta hacer el POST a la API.
    Lanza excepción si falla.
    """
    r = urequests.post(LOG_URL,
                       json=evento,
                       headers={"Content-Type": "application/json"})
    if r.json().get("ok") is not True:
        raise Exception("El servidor no aceptó el evento")
    r.close()



def log_acceso(uid, metodo):
    """
    Envia un acceso o lo encola si no hay conexión.
    """
    evento = {"uid": uid, "metodo": metodo}
    try:
        _intenta_enviar(evento)
        print("📬 Evento enviado OK")
    except Exception as e:
        print("⚠️  Error al enviar, encolando:", e)
        pendientes.append(evento)


def flush_pendientes():
    """
    Reintenta enviar todos los eventos encolados.
    Llama esta función periódicamente en tu main loop.
    """
    ok = 0
    for _ in range(len(pendientes)):
        evento = pendientes[0]
        try:
            _intenta_enviar(evento)
            pendientes.popleft()
            ok += 1
        except Exception:
            break  # si falla, no intentes más por ahora
    if ok:
        print(f"✔ Flushed {ok} eventos pendientes")
