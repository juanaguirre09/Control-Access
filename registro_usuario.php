<?php
// --- Proceso de guardado ---
$mensaje = "";
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nombre      = trim($_POST["nombre"]      ?? "");
    $pin         = trim($_POST["pin"]         ?? "");
    $rfid_uid    = trim($_POST["rfid_uid"]    ?? "");   // puede llegar vacío
    $slot_huella = trim($_POST["slot_huella"] ?? "");   // opcional

    // Validar campos obligatorios
    if ($nombre === "" || !preg_match('/^\d{4}$/', $pin)) {
        $mensaje = "Por favor, ingresa el nombre y una clave de 4 dígitos.";
    } else {
        $conn = new mysqli("localhost", "root", "", "control_acceso");
        if ($conn->connect_error) {
            $mensaje = "Error de conexión a la base de datos.";
        } else {
            /* ---------- INSERT con estado_huella = 'pendiente' ---------- */
            $sql = "INSERT INTO usuarios
                    (nombre, pin, rfid_uid, slot_huella, estado_huella)
                    VALUES (?, ?, ?, ?, 'pendiente')";
            $stmt = $conn->prepare($sql);

            // Convertir "" → NULL
            $rfid_val        = ($rfid_uid    !== "") ? $rfid_uid            : null;
            $slot_huella_val = ($slot_huella !== "") ? intval($slot_huella) : null;

            /* 4 parámetros: nombre, pin, rfid_uid/NULL, slot/NULL */
            $stmt->bind_param(
                "sssi",          // s = string, s = string, s = string|NULL, i = int|NULL
                $nombre,
                $pin,
                $rfid_val,
                $slot_huella_val
            );

            if ($stmt->execute()) {
                $mensaje = "✅ Usuario registrado correctamente.";
            } else {
                $mensaje = "Error al registrar usuario: " . $stmt->error;
            }
            $stmt->close();
            $conn->close();
        }
    }
}
?>


<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Registro de Nuevo Usuario - Proyecto Microcontroladores 2</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            background: #f2f4f8;
        }
        .container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 24px 5vw 0 5vw;
            background: #fff;
            border-bottom: 1px solid #ddd;
        }
        .header img {
            height: 56px;
            margin-right: 20px;
        }
        .header-title {
            font-size: 2.2em;
            font-weight: bold;
            color: #233e8b;
            margin: 0;
        }
        .content-center {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        form {
            background: #fff;
            padding: 32px 32px 24px 32px;
            border-radius: 16px;
            box-shadow: 0 4px 16px 0 #233e8b22;
            min-width: 340px;
            margin-top: 32px;
        }
        label { 
            display: block; 
            margin-top: 12px;
            font-weight: 500;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 7px;
            margin-top: 3px;
            border-radius: 6px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            font-size: 1em;
        }
        input[type="submit"] {
            margin-top: 18px; 
            padding: 9px 28px;
            background: #233e8b;
            color: #fff;
            border: none;
            border-radius: 7px;
            font-weight: bold;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.2s;
        }
        input[type="submit"]:hover {
            background: #4063bb;
        }
        .msg {
            margin-top: 18px; 
            font-weight: bold; 
            color: #185618;
            background: #e5ffe5;
            border: 1px solid #b8f6b8;
            padding: 8px 14px;
            border-radius: 7px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="logo.png" alt="Logo">
            <span class="header-title">Proyecto final microcontroladores 2 - sistema de control de acceso</span>
        </div>
        <div class="content-center">
            <form method="post" autocomplete="off">
                <h2 style="margin-bottom:14px; color:#233e8b;">Registro de Nuevo Usuario</h2>
                <label>Nombre*:
                    <input type="text" name="nombre" maxlength="50" required>
                </label>
                <label>Clave (4 dígitos)*:
                    <input type="text" name="pin" pattern="\d{4}" maxlength="4" required title="Debe ser un número de 4 dígitos">
                </label>
                <label>UID RFID (opcional):
                    <input type="text" name="rfid_uid" maxlength="32">
                </label>
                <label>Slot Huella (opcional):
                    <input type="number" name="slot_huella" min="1" max="199">
                </label>
                <input type="submit" value="Registrar">
                <?php if($mensaje): ?>
                    <div class="msg"><?= htmlspecialchars($mensaje) ?></div>
                <?php endif; ?>
            </form>
        </div>
    </div>
</body>
</html>
