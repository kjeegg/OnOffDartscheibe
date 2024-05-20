<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Spiel - Dartscheibe</title>
    <style>
        body {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .container {
            text-align: center;
            margin-top: 50px;
        }
        .scoreboard {
            display: flex;
            justify-content: space-around;
            margin-top: 50px;
        }
        .player {
            text-align: center;
        }
        .score {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .circle {
            width: 200px;
            height: 200px;
            border: 10px solid #17a2b8;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }
        .actions {
            margin-top: 20px;
        }
        footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 10px;
            background-color: #1a1a1a;
            color: #ffffff;
        }
    </style>
</head>
<body>
<nav class="navbar navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Dartscheibe</a>
        <div class="d-flex">
            <a href="#" class="nav-link text-light">Spielen</a>
            <a href="#" class="nav-link text-light">Statistik</a>
            <a href="#" class="nav-link text-light">Login</a>
        </div>
    </div>
</nav>

<div class="container">
    <div class="scoreboard">
        <div class="player" id="player1">
            <div class="circle">
                <div class="score" id="score1">124</div>
            </div>
            <div>Spieler 1</div>
            <textarea class="form-control mt-3" rows="3" id="notes1" placeholder="Notizen..."></textarea>
        </div>
        <div class="player" id="player2">
            <div class="circle">
                <div class="score" id="score2">76</div>
            </div>
            <div>Spieler 2</div>
            <textarea class="form-control mt-3" rows="3" id="notes2" placeholder="Notizen..."></textarea>
        </div>
    </div>
</div>

<footer>
    <a href="/kontakt">Kontakt</a> |
    <a href="/impressum">Impressum</a> |
    <a href="/datenschutz">Datenschutz</a>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
    async function loadGame() {
        const gameId = "your_game_id"; // Replace with actual game ID
        try {
            const response = await fetch(`https://api.onoff-dart.de/game/${gameId}/display`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const game = await response.json();
            console.log('Game data:', game);
            document.getElementById('score1').textContent = game.player[0].score.Score;
            document.getElementById('score2').textContent = game.player[1].score.Score;
            // Update other UI elements as necessary
        } catch (error) {
            console.error('Fehler beim Laden des Spiels:', error);
            alert('Fehler beim Laden des Spiels: ' + error.message);
        }
    }

    window.onload = loadGame;
</script>
</body>
</html>
