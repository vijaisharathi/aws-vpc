<?php
header('Content-Type: application/json');
header('Cache-Control: no-cache, no-store, must-revalidate');

$configFile = '/var/www/html/network-config.json';
$config = [];
if (file_exists($configFile)) {
    $config = json_decode(file_get_contents($configFile), true) ?: [];
}

$dbHost = isset($config['db_host']) ? trim($config['db_host']) : '';
$dbName = isset($config['db_name']) ? trim($config['db_name']) : 'academicdb';
$dbUser = isset($config['db_user']) ? trim($config['db_user']) : 'dbadmin';
$dbPass = isset($config['db_pass']) ? trim($config['db_pass']) : '';

// Truthfully verify configuration presence
if (empty($dbHost) || $dbHost === 'pending' || $dbHost === 'None') {
    echo json_encode([
        'connected' => false,
        'status'    => 'standby',
        'host'      => 'Pending / Disabled',
        'database'  => $dbName,
        'message'   => 'RDS MySQL endpoint is not configured or instance is in standby mode.',
        'timestamp' => date('Y-m-d H:i:s T')
    ], JSON_PRETTY_PRINT);
    exit;
}

// Attempt real TCP / MySQL handshake over private VPC routing with a strict 2-second timeout
try {
    $dsn = "mysql:host={$dbHost};port=3306;dbname={$dbName};charset=utf8mb4";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_TIMEOUT            => 2,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ];

    $pdo = new PDO($dsn, $dbUser, $dbPass, $options);
    
    // Execute a lightweight query to confirm responsiveness
    $stmt = $pdo->query('SELECT VERSION() AS mysql_ver, DATABASE() AS cur_db');
    $row = $stmt->fetch();

    echo json_encode([
        'connected' => true,
        'status'    => 'connected',
        'host'      => $dbHost,
        'database'  => $dbName,
        'version'   => isset($row['mysql_ver']) ? $row['mysql_ver'] : 'MySQL 8.0',
        'message'   => 'Successfully established authenticated session across VPC private subnets on Port 3306.',
        'timestamp' => date('Y-m-d H:i:s T')
    ], JSON_PRETTY_PRINT);

} catch (PDOException $e) {
    // Truthful report of failure without leaking passwords or sensitive stack traces
    $errorMessage = 'Connection refused or timed out. Ensure RDS instance is fully available and Security Group allows port 3306 from Web SG.';
    
    // Differentiate between authentication failure vs network unreachable
    if ($e->getCode() == 1045) {
        $errorMessage = 'Network route verified (Port 3306 reachable), but authentication failed with provided database credentials.';
    } elseif ($e->getCode() == 2002) {
        $errorMessage = 'Network route or host unreachable on Port 3306. Check RDS initialization state and security group ingress chaining.';
    }

    echo json_encode([
        'connected' => false,
        'status'    => 'disconnected',
        'host'      => $dbHost,
        'database'  => $dbName,
        'message'   => $errorMessage,
        'timestamp' => date('Y-m-d H:i:s T')
    ], JSON_PRETTY_PRINT);
}

