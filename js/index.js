async function getHighestGameUID() {
    try {
        const response = await fetch('http://localhost:8000/api/game', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const games = await response.json();
        let highestUID = 0;
        games.forEach(game => {
            if (game.uid > highestUID) {
                highestUID = game.uid;
            }
        });
        return highestUID;
    } catch (error) {
        console.error('Fehler beim Laden der Spiele:', error);
        alert('Fehler beim Laden der Spiele: ' + error.message);
        return null;
    }
}

document.getElementById('createGameForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const highestUID = await getHighestGameUID();
    if (highestUID === null) {
        alert('Fehler beim Erstellen des neuen Spiels');
        return;
    }

    const newGameId = String(parseInt(highestUID) + 1);
    const player1Id = parseInt(document.getElementById('player1Id').value);
    const player2Id = parseInt(document.getElementById('player2Id').value);

    const gameData = {
        "uid": newGameId,
        "player": [player1Id, player2Id],
        "game": "x01",
        "variant": "501",
        "in": "straight",
        "out": "double",
        "sound": true,
        "podium": false,
        "autoswitch": false,
        "cricketrandom": false,
        "cricketghost": false
    };

    try {
        const response = await fetch(`http://localhost:8000/api/game/${newGameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(gameData)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        alert('Spiel erfolgreich erstellt!');
        window.location.href = `spiel.html?gameId=${newGameId}`;
    } catch (error) {
        alert('Fehler beim Erstellen des Spiels: ' + error.message);
    }
});

document.getElementById('joinGameForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const gameId = document.getElementById('joinGameId').value;

    try {
        const response = await fetch(`http://localhost:8000/api/game/${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        alert('Spiel beigetreten!');
        window.location.href = `spiel.html?gameId=${gameId}`;
    } catch (error) {
        alert('Fehler beim Beitreten des Spiels: ' + error.message);
    }
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Simple admin login check for demonstration purposes
    if (username === 'admin' && password === 'admin123') {
        window.location.href = 'admin.html';
    } else {
        alert('Falscher Benutzername oder Passwort');
    }
});

document.getElementById('addPlayerForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const playerName = document.getElementById('playerName').value;
    // const playerNickname = document.getElementById('playerNickname').value;

    const playerData = {
        "name": playerName,
        // "nickname": playerNickname
    };

    try {
        const response = await fetch('http://localhost:8000/api/player', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(playerData)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        alert('Spieler ID: ' + data.UID);
        console.log(data.UID);
        document.getElementById('addPlayerForm').reset();
    } catch (error) {
        alert('Fehler beim Hinzufügen des Spielers: ' + error.message);
    }
});

window.onload = function() {
    if (!getCookie('cookieConsent')) {
        document.getElementById('cookieConsent').style.display = 'block';
    }
};

function acceptCookies() {
    document.getElementById('cookieConsent').style.display = 'none';
    setCookie('cookieConsent', 'true', 365);
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}