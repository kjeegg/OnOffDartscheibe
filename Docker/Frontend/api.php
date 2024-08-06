<?php
header('Content-Type: application/json');


$apiBaseUrl = 'http://localhost:8000/api';

function forwardRequest($apiFunction, $queryParams = '', $method = 'GET', $body = null) {
    global $apiBaseUrl;

    $url = $apiBaseUrl . $apiFunction . $queryParams;

    $options = [
        'http' => [
            'method' => $method,
            'header' => 'Content-Type: application/json'
        ]
    ];

    if ($body) {
        $options['http']['content'] = json_encode($body);
    }

    $context = stream_context_create($options);
    $response = file_get_contents($url, false, $context);

    if ($response === FALSE) {
        $error = error_get_last();
        http_response_code(500);
        echo json_encode([
            'error' => 'Error occurred while forwarding the request',
            'details' => $error['message'],
            'url' => $url,
            'method' => $method,
            'body' => $body,
            'http_response_header' => isset($http_response_header) ? $http_response_header : null
        ]);
        return;
    }

    echo $response;
}
// Handle the API request
if (isset($_GET['apiFunction'])) {
    $apiFunction = $_GET['apiFunction'];
    $queryParams = '';

    switch ($apiFunction) {
        case 'getHighestGameUID':
            forwardRequest('/game');
            break;
        case 'createGame':
            $queryParams = '/' . $_GET['gameId'];
            $body = json_decode(file_get_contents('php://input'), true);
            forwardRequest('/game' . $queryParams, '', 'POST', $body);
            break;
        case 'getGame':
            $queryParams = '/' . $_GET['gameId'];
            forwardRequest('/game' . $queryParams);
            break;
        case 'addPlayer':
            $body = json_decode(file_get_contents('php://input'), true);
            forwardRequest('/player', '', 'POST', $body);
            break;
        case 'getTopPlayers':
            forwardRequest('/player');
            break;
        case 'getAllGames':
            forwardRequest('/game');
            break;
        case 'getGameDisplay':
            $queryParams = '/' . $_GET['gameId'] . '/display';
            forwardRequest('/game' . $queryParams);
            break;
        case 'nextPlayer':
            $queryParams = '/' . $_GET['gameId'] . '/nextPlayer';
            forwardRequest('/game' . $queryParams, '', 'POST');
            break;
        case 'manualEntry':
            $body = json_decode(file_get_contents('php://input'), true);
            $queryParams = '/' . $_GET['gameId'] . '/throw/' . $body['number'] . '/' . $body['modifier'];
            forwardRequest('/game' . $queryParams, '', 'POST');
            break;
        case 'endGame':
            $queryParams = '/' . $_GET['gameId'];
            forwardRequest('/game' . $queryParams, '', 'DELETE');
            break;
        default:
            echo json_encode(['error' => 'Invalid function specified']);
            break;
    }
} else {
    echo json_encode(['error' => 'No function specified']);
}
?>
