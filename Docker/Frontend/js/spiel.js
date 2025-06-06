// fireworks
const container = document.querySelector('.fireworks-container');
const fireworks = new Fireworks.default(container);

// Script Version
console.log("Version: 0.2.3");

async function loadGame() {
    const gameId = getGameId();

    try {
        const response = await fetch(`api.php?apiFunction=getGameDisplay&gameId=${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const game = await response.json();
        updateGameDisplay(game);
        updatePlayerTurn(game);
        setLast3Throws(game);
        
        // Check if game is finished
        // Can be done with GameState instead
        if (game.Player[0].Score?.Score === 0 || game.Player[1].Score?.Score === 0) {
            displayWinner(game);
        }
        
        // Clear last throws if player switched
        if (game.GameState === "THROW" && game.Player[game.ActivePlayer].LastThrows.length === 3) {
            clearLast3Throws(game.ActivePlayer);
        }
        // Check for bust
        if (game.GameState === "BUST") {
            bust(game, false);
        } else if (game.GameState === "BUSTNOCHECKOUT") {
            bust(game, true);
        }
        
    } catch (error) {
        console.error('Fehler beim Laden des Spiels:', error);
    }
}
function getGameId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('gameId');
}

//* For future use: Don't call every function inside the fetch request
// Better yet: Don't use this frontend, use react or sumn
async function getGameById(gameId) {
    try {
        const response = await fetch(`api.php?apiFunction=getGameDisplay&gameId=${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const game = await response.json();
        return game;
    } catch (error) {
        console.error('Fehler beim Laden des Spiels:', error);
    }
}


function setLast3Throws(game) {
    // i is player, j is throw
    for (let i = 0; i <= 1; i++) {
        for (let j = 0 ; j <= game.Player[i].LastThrows.length - 1; j++) {
            const throwElement = document.getElementById(`throw-${i}-${j + 1}`);
            if (game.Player[i].LastThrows[j].Number === 0) {
                throwElement.textContent = "X";
            } else {
                throwElement.textContent = `${game.Player[i].LastThrows[j].Number * game.Player[i].LastThrows[j].Modifier}`;
            }
        }
    }
}

function clearLast3Throws(player) {
    for (let i = 1; i <= 3; i++) {
        const throwElement = document.getElementById(`throw-${player}-${i}`);
        throwElement.innerHTML = '';
        // console.log('Cleared throw-' + player + '-' + i);
    }
}

// Inserts name and score of players
function updateGameDisplay(game) {

    if (!game || !game.Player || game.Player.length === 0) {
        console.error('Invalid game data:', game);
        return;
    }

    // Updating Player 1
    const player1 = game.Player[0];
    const player1Name = document.getElementById('player1Name');
    const player1Score = document.getElementById('score1');

    player1Name.textContent = player1.Name;
    player1Score.textContent = player1.Score?.Score || 0;
    
    // Updating Player 2 if exists
    if (game.Player.length > 1) {
        const player2 = game.Player[1];
        const player2Name = document.getElementById('player2Name');
        const player2Score = document.getElementById('score2');

        player2Name.textContent = player2.Name;
        player2Score.textContent = player2.Score?.Score || 0;
    }
    previousGameData = game;
}

async function deleteLastThrows() {
    const gameId = getGameId();
    try {
        const response = await fetch(`api.php?apiFunction=deleteLastThrows&gameId=${gameId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        loadGame();
    } catch (error) {
        console.error('Fehler beim Löschen der letzten Würfe:', error);
    }

}

// Handle invalid throws (never used lmao)
function handleInvalidThrow(throwData) {
    const throwValue = throwData.Number * throwData.Modifier;
    if (throwValue === 0) {
        console.log('Invalid throw. ill not be recorded.');
        return false;
    }
    return true;
}

// Gets game variant and out, displays it as title
document.addEventListener('DOMContentLoaded', function() {
    loadTitle();
});
async function loadTitle() {
    const gameId = getGameId();
    try {
        const response = await fetch(`api.php?apiFunction=getGameDisplay&gameId=${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const game = await response.json();
        document.getElementById('game-variant').textContent = game.Variant || '501';
        document.getElementById('game-out').textContent = game.Out + ' out';
    } catch (error) {
        console.error('Fehler beim Laden des Spiels:', error);
    }
}

// nextPlayer: fetch game and nextPlayer API, update last 3 throws, loadGame
async function nextPlayer() {
    const gameId = getGameId();
    // get game
    try {
        const response = await fetch(`api.php?apiFunction=getGameDisplay&gameId=${gameId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const game = await response.json();
        ActivePlayer = game.ActivePlayer;
    } catch (error) {
        console.error('Fehler beim Laden des Spiels:', error);
    }
    // send nextPlayer request
    try {
        await fetch(`api.php?apiFunction=nextPlayer&gameId=${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Fehler beim Spielerwechsel:', error);
    }
    console.log('Last ActivePlayer: ' + ActivePlayer);
    loadGame();
}

var bustModal = new bootstrap.Modal(document.getElementById("bustModal"));
/**
 * 
 * @param {GameObject} game 
 * @param {bool} nocheckout 
 */

function bust(game, nocheckout = false) {
    if (nocheckout) {
        document.getElementById('bust-dialog').textContent = game.Player[game.ActivePlayer].Name + " kann nicht auschecken!";
    } else {
        document.getElementById('bust-dialog').textContent = game.Player[game.ActivePlayer].Name + "'s Punkte wurden zurückgesetzt!";
    }
    bustModal.show();
}

/* 
    GAME BUTTONS
*/

async function skipTurn() {
    nextPlayer();
    console.log('Turn skipped');
}
const skipButton = document.getElementById('skip-turn');
skipButton.addEventListener('click', skipTurn);

// manualEntry
document.getElementById('manualEntryForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const gameId = getGameId();

    const points = parseInt(document.getElementById('manualEntryPoints').value);
    const modifier = parseInt(document.getElementById('manualEntryModifier').value);
    // TODO: Validate points and modifier
    try {
        const response = await fetch(`api.php?apiFunction=manualEntry&gameId=${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                number: points, 
                modifier: modifier })
        });
        console.log('Response:', response);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        document.getElementById('manualEntryForm').reset();
        loadGame();
    } catch (error) {
        console.error('Fehler beim manuellen Eintragen:', error);
    }
});
const manualEntryButton = document.getElementById('manual-entry');
manualEntryButton.addEventListener('click', loadGame());

async function endGame() {
    const gameId = getGameId();
    if (!confirm('Spiel wirklich beenden?')) {
        return;
    }
    try {
        const response = await fetch(`api.php?apiFunction=endGame&gameId=${gameId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        window.location.href = 'index.html';
    } catch (error) {
        console.error('Fehler beim Beenden des Spiels:', error);
        alert('Fehler beim Beenden des Spiels: ' + error.message);
    }
}
document.querySelectorAll('.end-game').forEach(button => button.addEventListener('click', endGame));

// display Winner (yes this is a mess)
var winModal = new bootstrap.Modal(document.getElementById("winModal"));
function displayWinner(game) {
    if(game.Player[0].Score?.Score === 0) {
        console.log('Winner: ' + game.Player[0].Name)
        document.getElementById('winner').textContent = game.Player[0].Name;
        document.getElementById('player1-box').style.boxShadow = '0 0 100px 0px #00b1ac';
        winModal.show();
        document.querySelector('.fireworks-container').style.display = 'block';
        fireworks.start();
    } else if(game.Player[1].Score?.Score === 0) {
        console.log('Winner: ' + game.Player[1].Name)
        document.getElementById('winner').textContent = game.Player[1].Name;
        document.getElementById('player2-box').style.boxShadow = '0 0 100px 0px #00b1ac';
        winModal.show();
        document.querySelector('.fireworks-container').style.display = 'block';
        fireworks.start();
    }
}

// Rotate the arrow in the middle and box-shadow the active player
function updatePlayerTurn(game) {
    if(game.ActivePlayer === 0) {
        document.getElementById('player1-box').classList.add('active');
        document.getElementById('player2-box').classList.remove('active');
        document.getElementById('arrow-wrapper').classList.remove('active');

    }
    else {
        document.getElementById('player1-box').classList.remove('active');
        document.getElementById('player2-box').classList.add('active');
        document.getElementById('arrow-wrapper').classList.add('active');
    }
}

// fetch all data from api every 2000 ms
window.onload = function() {
    loadGame();
    setInterval(loadGame, 2000); // Update interval
};