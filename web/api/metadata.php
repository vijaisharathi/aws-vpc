<?php
header('Content-Type: application/json');
header('Cache-Control: no-cache, no-store, must-revalidate');

// Read static network topology generated during deployment
$configFile = '/var/www/html/network-config.json';
$config = [];
if (file_exists($configFile)) {
    $configJson = file_get_contents($configFile);
    $config = json_decode($configJson, true) ?: [];
}

// Helper to query EC2 IMDSv2 safely with short timeout
function getImdsData($path) {
    $tokenUrl = 'http://169.254.169.254/latest/api/token';
    $ch = curl_init($tokenUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['X-aws-ec2-metadata-token-ttl-seconds: 60']);
    curl_setopt($ch, CURLOPT_TIMEOUT_MS, 300);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT_MS, 300);
    $token = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($status !== 200 || !$token) {
        return null;
    }

    $metaUrl = 'http://169.254.169.254/latest/meta-data/' . ltrim($path, '/');
    $ch = curl_init($metaUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['X-aws-ec2-metadata-token: ' . $token]);
    curl_setopt($ch, CURLOPT_TIMEOUT_MS, 300);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT_MS, 300);
    $val = curl_exec($ch);
    $metaStatus = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    return ($metaStatus === 200 && $val) ? trim($val) : null;
}

// Fetch IMDSv2 values or fall back to system defaults
$instanceId = getImdsData('instance-id') ?: (isset($config['instance_id']) ? $config['instance_id'] : 'i-simulated');
$az         = getImdsData('placement/availability-zone') ?: (isset($config['availability_zone']) ? $config['availability_zone'] : 'us-east-1a');
$instanceType = getImdsData('instance-type') ?: (isset($config['instance_type']) ? $config['instance_type'] : 't2.micro');
$privateIp  = getImdsData('local-ipv4') ?: (isset($_SERVER['SERVER_ADDR']) ? $_SERVER['SERVER_ADDR'] : '10.0.1.x');
$publicIp   = getImdsData('public-ipv4') ?: 'Dynamic / Public';
$amiId      = getImdsData('ami-id') ?: 'Ubuntu 22.04 LTS (Jammy)';

// Uptime calculation
$uptime = 'Active';
if (is_readable('/proc/uptime')) {
    $uptimeSecs = (int)floatval(file_get_contents('/proc/uptime'));
    $days = floor($uptimeSecs / 86400);
    $hours = floor(($uptimeSecs % 86400) / 3600);
    $minutes = floor(($uptimeSecs % 3600) / 60);
    $uptime = "{$days}d {$hours}h {$minutes}m";
}

$response = [
    'project_title'          => isset($config['project_title']) ? $config['project_title'] : 'AWS VPC – Public and Private Subnet Demonstration',
    'vpc_cidr'               => isset($config['vpc_cidr']) ? $config['vpc_cidr'] : '10.0.0.0/16',
    'public_subnet_cidr'     => isset($config['public_subnet_cidr']) ? $config['public_subnet_cidr'] : '10.0.1.0/24',
    'private_subnet_1_cidr'  => isset($config['private_subnet_1_cidr']) ? $config['private_subnet_1_cidr'] : '10.0.2.0/24',
    'private_subnet_2_cidr'  => isset($config['private_subnet_2_cidr']) ? $config['private_subnet_2_cidr'] : '10.0.3.0/24',
    'instance_id'            => $instanceId,
    'availability_zone'      => $az,
    'instance_type'          => $instanceType,
    'private_ip'             => $privateIp,
    'public_ip'              => $publicIp,
    'ami_id'                 => $amiId,
    'uptime'                 => $uptime,
    'system_load'            => function_exists('sys_getloadavg') ? implode(' ', array_map(function($v) { return round($v, 2); }, sys_getloadavg())) : 'Normal',
    'server_time'            => date('Y-m-d H:i:s T')
];

echo json_encode($response, JSON_PRETTY_PRINT);

