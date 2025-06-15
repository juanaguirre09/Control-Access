<?php
header('Content-Type: application/json');

// 1. Conexión
$conn = new mysqli('localhost', 'root', '', 'control_acceso');
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'DB connect']);
    exit;
}

// 2. Leer cuerpo JSON
$entrada = json_decode(file_get_contents('php://input'), true);
$uid    = $entrada['uid']    ?? '';
$metodo = $entrada['metodo'] ?? '';

if (!$uid || !$metodo) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Bad request']);
    exit;
}

// 3. Insertar registro
$stmt = $conn->prepare(
    'INSERT INTO registros (uid, metodo) VALUES (?, ?)'
);
$stmt->bind_param('ss', $uid, $metodo);
$stmt->execute();

echo json_encode(['ok' => true, 'id' => $stmt->insert_id]);
?>