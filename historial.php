<?php
/******************* 1) CONEXIÓN *************************/
$conn = new mysqli("localhost", "root", "", "control_acceso");
if ($conn->connect_error) die("Error de conexión");

/******************* 2) FILTRO Y PÁGINA ACTUAL ***********/
$perPage = 50;                                   // registros por página
$page    = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$offset  = ($page - 1) * $perPage;
$filtro  = trim($_GET['buscar'] ?? "");

/******************* 3) CONSULTA PRINCIPAL ***************/
$sqlBase = "
  FROM registros
  LEFT JOIN usuarios
         ON (registros.metodo = 'tarjeta' AND registros.uid = usuarios.rfid_uid)
        OR (registros.metodo = 'huella'  AND registros.uid = usuarios.slot_huella)
        OR (registros.metodo = 'clave'   AND registros.uid = usuarios.id)
";

$where   = "";
$params  = [];
$types   = "";

if ($filtro !== "") {
    $where  = " WHERE usuarios.nombre LIKE ? OR registros.uid LIKE ? ";
    $like   = "%$filtro%";
    $params = [&$like, &$like];
    $types  = "ss";
}

/* --- principal (con LIMIT) --- */
$sqlListado = "SELECT registros.*, usuarios.nombre " . $sqlBase . $where .
              " ORDER BY registros.momento DESC LIMIT ? OFFSET ?";

$params[] = &$perPage;
$params[] = &$offset;
$types   .= "ii";

$stmt = $conn->prepare($sqlListado);
$stmt->bind_param($types, ...$params);
$stmt->execute();
$result = $stmt->get_result();

/* --- total filas para paginación --- */
$sqlCount = "SELECT COUNT(*) AS total " . $sqlBase . $where;
$countStmt = $conn->prepare($sqlCount);
if ($filtro !== "") {
    $countStmt->bind_param("ss", $like, $like);
}
$countStmt->execute();
$totalRows = $countStmt->get_result()->fetch_assoc()['total'] ?? 0;
$totalPages = ceil($totalRows / $perPage);
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Histórico de Ingresos</title>
<style>
    body        { font-family: Arial, sans-serif; background:#f2f4f8; margin:0;}
    .container  { max-width:950px; margin:32px auto; background:#fff;
                  border-radius:10px; padding:30px 40px 25px;
                  box-shadow:0 4px 16px #233e8b22; }
    h2          { color:#233e8b; margin-top:0;}
    table       { width:100%; border-collapse:collapse; margin-top:18px;}
    th,td       { padding:8px 12px; border-bottom:1px solid #dbe3ef; text-align:center;}
    th          { background:#233e8b; color:#fff;}
    tr:nth-child(even){ background:#f5f8ff;}
    .filtro     { margin-top:12px;}
    input[type="text"]  { padding:6px; border-radius:5px; border:1px solid #bbb;}
    input[type="submit"]{ padding:6px 14px; background:#233e8b; color:#fff;
                          border:none; border-radius:5px; cursor:pointer;}
    input[type="submit"]:hover{ background:#4063bb;}
    .btn        { display:inline-block; margin-top:18px; padding:8px 18px;
                  background:#0064d6; color:#fff; text-decoration:none;
                  border-radius:6px; font-weight:bold;}
    .btn:hover  { background:#004ea8;}
    nav a       { margin:0 4px; text-decoration:none; color:#233e8b;}
    nav a[aria-current]{ font-weight:bold; text-decoration:underline;}
</style>
</head>
<body>
<div class="container">
    <h2>Histórico de Ingresos</h2>

    <!-- Botón de registro -->
    <a class="btn" href="registro_usuario.php">Registrar nuevo usuario</a>

    <!-- Formulario de filtro -->
    <form method="get" class="filtro">
        <label>Buscar por Nombre o ID:
            <input type="text" name="buscar"
                   value="<?= htmlspecialchars($filtro) ?>"
                   placeholder="Ej: Claudia o 26DB3B02C4">
        </label>
        <input type="submit" value="Filtrar">
        <?php if ($filtro !== ""): ?>
            <a href="historial.php" style="margin-left:16px;">Limpiar filtro</a>
        <?php endif; ?>
    </form>

    <!-- Tabla -->
    <table>
        <tr>
            <th>Nombre</th>
            <th>ID</th>
            <th>Método</th>
            <th>Fecha y Hora</th>
        </tr>
        <?php while ($row = $result->fetch_assoc()): ?>
        <tr>
            <td><?= htmlspecialchars($row["nombre"] ?? "Desconocido") ?></td>
            <td><?= htmlspecialchars($row["uid"]) ?></td>
            <td><?= ucfirst(htmlspecialchars($row["metodo"])) ?></td>
            <td><?= htmlspecialchars($row["momento"]) ?></td>
        </tr>
        <?php endwhile; ?>
    </table>

    <!-- Navegación de páginas -->
    <?php if ($totalPages > 1): ?>
        <nav style="margin-top:16px;">
            <?php
            // conserva cualquier filtro en los links
            $baseQuery = $filtro !== "" ? "buscar=" . urlencode($filtro) . "&" : "";
            // botón «Anterior»
            if ($page > 1) {
                echo '<a href="?' . $baseQuery . 'page=' . ($page-1) . '">«</a>';
            }
            // números
            for ($i = 1; $i <= $totalPages; $i++) {
                $attr = $i == $page ? 'aria-current="page"' : '';
                echo '<a ' . $attr . ' href="?' . $baseQuery . 'page=' . $i . '">' . $i . '</a>';
            }
            // botón «Siguiente»
            if ($page < $totalPages) {
                echo '<a href="?' . $baseQuery . 'page=' . ($page+1) . '">»</a>';
            }
            ?>
        </nav>
    <?php endif; ?>
</div>
</body>
</html>
<?php
$stmt->close();
$countStmt->close();
$conn->close();
?>
