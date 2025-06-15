<?php
header('Content-Type: application/json');

// 1) Leer JSON de la petición
$data = json_decode(file_get_contents('php://input'), true);
$userId = intval($data['user'] ?? 0);
$slot   = $data['slot'] ?? null;

if (!$userId) {
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>'user obligatorio']);
    exit;
}

// 2) Conexión BD
$conn = new mysqli("localhost","root","","control_acceso");
if ($conn->connect_error) {
    echo json_encode(['ok'=>false,'error'=>'DB error']);
    exit;
}

// 3) ¿Existe el usuario y está pendiente?
$user = $conn->query("SELECT slot_huella, estado_huella FROM usuarios WHERE id=$userId")->fetch_assoc();
if (!$user) {
    echo json_encode(['ok'=>false,'error'=>'Usuario no existe']);
    exit;
}
if ($user['estado_huella'] === 'ok') {
    echo json_encode(['ok'=>false,'error'=>'Ya enrolado']);
    exit;
}

// 4) Si no tiene slot, buscamos uno libre (0-199)
if ($user['slot_huella'] === null) {
    $res   = $conn->query("SELECT MAX(slot_huella)+1 AS next FROM usuarios WHERE slot_huella IS NOT NULL");
    $slot  = intval($res->fetch_assoc()['next'] ?? 0);
    if ($slot > 199) $slot = -1;                // sin espacio
    // guardamos provisionalmente
    $conn->query("UPDATE usuarios SET slot_huella=$slot WHERE id=$userId");
} else {
    $slot = intval($user['slot_huella']);
}

// 5) Llamar al ESP32
$esp32_ip = "192.168.0.8";      // ⇠ ajusta tu IP
$url      = "http://$esp32_ip/enroll";
$payload  = json_encode(['slot'=>$slot]);

$ctx = stream_context_create([
  'http'=>[
    'method'  => 'POST',
    'header'  => "Content-Type: application/json\r\n".
                 "Content-Length: ".strlen($payload)."\r\n",
    'content' => $payload,
    'timeout' => 15
  ]
]);

$response = @file_get_contents($url, false, $ctx);
if ($response === false) {
    echo json_encode(['ok'=>false,'error'=>'ESP32 no responde']);
    exit;
}
$resp = json_decode($response, true);

// 6) Evaluar respuesta
if ($resp['ok'] ?? false) {
    $conn->query("UPDATE usuarios
                  SET estado_huella='ok'
                  WHERE id=$userId");
    echo json_encode(['ok'=>true]);
} else {
    echo json_encode(['ok'=>false,'error'=>$resp['error'] ?? 'Enrol falló']);
}
