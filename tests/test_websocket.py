from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_websocket_echo():
    """Se conecta a un websocket y verifica el mensaje de eco."""
    with client.websocket_connect("/ws") as websocket:
        # Registrar dispositivo enviando joinRoom
        websocket.send_json({"deviceId": "test-device", "event": "joinRoom"})
        # Mensaje de bienvenida
        welcome = websocket.receive_json()
        assert welcome["type"] == "connection"
        assert welcome["connected_devices"] == 1

        # Enviar mensaje y recibir eco
        original_message = "hola"
        websocket.send_text(original_message)
        response = websocket.receive_json()

        assert response["type"] == "echo"
        assert response["original_message"] == original_message
        assert response["device_id"] == "test-device"


def test_broadcast_requires_room():
    """Intentar enviar sin room_id debe retornar error 422."""
    payload = {"message": "hola", "sender_id": "server"}
    response = client.post("/broadcast", json=payload)
    # Pydantic validation error -> 422
    assert response.status_code == 422


def test_websocket_direct_message():
    """Envía mensaje a un dispositivo específico y verifica que solo ese lo reciba."""
    with client.websocket_connect("/ws") as ws1:
        ws1.send_json({"deviceId": "device1", "event": "joinRoom"})
        ws1.receive_json()  # welcome
        with client.websocket_connect("/ws") as ws2:
            ws2.send_json({"deviceId": "device2", "event": "joinRoom"})
            ws2.receive_json()

            payload = {
                "message": "hola solo device1",
                "sender_id": "server",
                "room_id": "device1",
            }
            response = client.post("/broadcast", json=payload)
            assert response.status_code == 200
            assert response.json()["recipients"] == 1

            # device1 debe recibir el mensaje
            direct_msg = ws1.receive_json()
            assert direct_msg["type"] == "broadcast"
            assert direct_msg["message"] == payload["message"]
            assert direct_msg["recipients"] == 1

            # device2 no debería recibir un mensaje adicional. Para evitar bloqueo, no leemos.
