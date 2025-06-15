<?php
header('Content-Type: application/json');
$conn = new mysqli('localhost', 'root', '', 'control_acceso');
if ($conn->connect_error) {
    echo json_encode(["ok" => false, "error" => "DB error"]);
    exit;
}

$pin = isset($_GET["pin"]) ? $_GET["pin"] : "";
if (!$pin) {
    echo json_encode(["ok" => false, "error" => "Falta pin"]);
    exit;
}

$sql = "SELECT id, nombre, rfid_uid, slot_huella 
        FROM usuarios 
        WHERE pin = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $pin);
$stmt->execute();
$stmt->store_result();

if ($stmt->num_rows > 0) {
    // 1) Liga los resultados a variables
    $stmt->bind_result($id, $nombre, $rfid_uid, $slot_huella);
    $stmt->fetch();
    // 2) Devuelve id y nombre (y el resto si quieres)
    echo json_encode([
        "ok"          => true,
        "id"          => $id,
        "nombre"      => $nombre,
        "rfid_uid"    => $rfid_uid,
        "slot_huella" => $slot_huella
    ]);
} else {
    echo json_encode(["ok" => false, "error" => "No encontrado"]);
}

$stmt->close();
$conn->close();
?>
