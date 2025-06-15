<?php
/*********** 1) CONEXIÓN ****************/
$conn = new mysqli("localhost", "root", "", "control_acceso");
if ($conn->connect_error) die("Error de conexión: " . $conn->connect_error);

/*********** 2) (Opcional) FILTRO ********/
$filtro = trim($_GET['buscar'] ?? "");

/*********** 3) CONSULTA DE USUARIOS *****/
$sql = "SELECT id, nombre, pin, rfid_uid, slot_huella, estado_huella
        FROM usuarios";
$params = [];
$types  = "";

if ($filtro !== "") {
    $sql .= " WHERE nombre LIKE ? OR rfid_uid LIKE ? ";
    $like   = "%$filtro%";
    $params = [&$like, &$like];
    $types  = "ss";
}

$sql .= " ORDER BY id DESC";       // último primero

$stmt = $conn->prepare($sql);
if ($types !== "") $stmt->bind_param($types, ...$params);
$stmt->execute();
$result = $stmt->get_result();
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Listado de usuarios</title>
<style>
    body        { font-family:Arial, sans-serif; background:#f2f4f8; margin:0;}
    .container  { max-width:960px; margin:36px auto; background:#fff;
                  padding:30px 40px; border-radius:10px;
                  box-shadow:0 4px 16px #0001; }
    h2          { margin-top:0; color:#233e8b;}
    table       { width:100%; border-collapse:collapse; margin-top:20px;}
    th,td       { padding:8px 10px; border-bottom:1px solid #dbe3ef; text-align:center;}
    th          { background:#233e8b; color:#fff;}
    tr:nth-child(even){ background:#f7faff; }
    .btn        { padding:6px 14px; background:#0064d6; color:#fff; border:none;
                  border-radius:6px; cursor:pointer; font-weight:bold;}
    .btn:disabled { opacity:.6; cursor:default;}
    nav a       { margin:0 4px; text-decoration:none; }
</style>
</head>
<body>
<div class="container">
    <h2>Usuarios registrados</h2>

    <!-- Formulario de búsqueda -->
    <form method="get">
        <label>Buscar:
            <input type="text" name="buscar" value="<?= htmlspecialchars($filtro) ?>">
        </label>
        <input type="submit" value="Filtrar">
        <?php if ($filtro !== ""): ?>
            <a href="usuarios.php" style="margin-left:16px;">Limpiar</a>
        <?php endif; ?>
    </form>

    <!-- Tabla de usuarios -->
    <table>
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>PIN</th>
            <th>UID RFID</th>
            <th>Slot huella</th>
            <th>Huella</th>
        </tr>
        <?php while ($row = $result->fetch_assoc()): ?>
        <tr>
            <td><?= $row['id'] ?></td>
            <td><?= htmlspecialchars($row['nombre']) ?></td>
            <td><?= htmlspecialchars($row['pin']) ?></td>
            <td><?= htmlspecialchars($row['rfid_uid'] ?: '—') ?></td>
            <td><?= $row['slot_huella'] !== null ? $row['slot_huella'] : '—' ?></td>

            <td>
            <?php if ($row['estado_huella'] === 'ok'): ?>
                ✅
            <?php else: ?>
                <button class="enroll-btn"
                        data-user="<?= $row['id'] ?>"
                        data-slot="<?= $row['slot_huella'] ?? '' ?>">
                    Enrolar
                </button>
            <?php endif; ?>
            </td>
        </tr>
        <?php endwhile; ?>
    </table>

    <!-- Enlace para crear nuevos usuarios -->
    <p style="margin-top:24px;">
        <a class="btn" href="registro_usuario.php">Registrar nuevo usuario</a>
    </p>
</div>

<!-- 2-B) JavaScript para el botón Enrolar -->
<script>
document.addEventListener('click', async (e) => {
  if (!e.target.matches('.enroll-btn')) return;

  const btn   = e.target;
  const user  = btn.dataset.user;
  const slot  = btn.dataset.slot || '';

  if (!confirm(`¿Enrolar huella para el usuario #${user}?`)) return;

  btn.disabled   = true;
  btn.textContent = '⏳ …';

  try {
    const ctrl = new AbortController();
    const timeoutId = setTimeout(() => ctrl.abort(), 60000);  // ⏱ 60 segundos

    const res  = await fetch('api_enroll.php', {
      method : 'POST',
      headers: { 'Content-Type':'application/json' },
      body   : JSON.stringify({ user, slot }),
      signal : ctrl.signal
    });

    alert("Coloca tu dedo en el sensor ahora");
    clearTimeout(timeoutId);  // si llega respuesta, se cancela el timeout
    const data = await res.json();

    if (data.ok) {
      alert('✓ Huella enrolada correctamente');
      location.reload();
    } else {
      throw new Error(data.error || 'Error desconocido');
    }
  } catch (err) {
    alert('❌ ' + err.message);
    btn.disabled   = false;
    btn.textContent = 'Enrolar';
  }

});
</script>
</body>
</html>
<?php
$stmt->close();
$conn->close();
?>
