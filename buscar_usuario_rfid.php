<?php
header('Content-Type: application/json');
$host = "localhost";
$user = "root";
$pass = "";
$db   = "control_acceso";

$rfid_uid = isset($_GET["rfid_uid"]) ? $_GET["rfid_uid"] : "";

if ($rfid_uid === "") {
    echo json_encode(["ok"=>false, "error"=>"Falta rfid_uid"]);
    exit;
}

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    echo json_encode(["ok"=>false, "error"=>"DB error"]);
    exit;
}

$sql = "SELECT nombre, pin, slot_huella FROM usuarios WHERE rfid_uid = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $rfid_uid);
$stmt->execute();
$stmt->store_result();

if ($stmt->num_rows > 0) {
    $stmt->bind_result($nombre, $pin, $slot_huella);
    $stmt->fetch();
    echo json_encode([
        "ok" => true,
        "nombre" => $nombre,
        "pin" => $pin,
        "slot_huella" => $slot_huella
    ]);
} else {
    echo json_encode(["ok"=>false, "error"=>"No encontrado"]);
}

$stmt->close();
$conn->close();
?>
