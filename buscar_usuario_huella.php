<?php
header('Content-Type: application/json');
$host = "localhost";
$user = "root";
$pass = "";
$db   = "control_acceso";

$slot = isset($_GET["slot"]) ? $_GET["slot"] : "";

if ($slot === "") {
    echo json_encode(["ok"=>false, "error"=>"Falta slot"]);
    exit;
}

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    echo json_encode(["ok"=>false, "error"=>"DB error"]);
    exit;
}

$sql = "SELECT nombre, rfid_uid, pin FROM usuarios WHERE slot_huella = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $slot);
$stmt->execute();
$stmt->store_result();

if ($stmt->num_rows > 0) {
    $stmt->bind_result($nombre, $rfid_uid, $pin);
    $stmt->fetch();
    echo json_encode([
        "ok" => true,
        "nombre" => $nombre,
        "rfid_uid" => $rfid_uid,
        "pin" => $pin
    ]);
} else {
    echo json_encode(["ok"=>false, "error"=>"No encontrado"]);
}

$stmt->close();
$conn->close();
?>
