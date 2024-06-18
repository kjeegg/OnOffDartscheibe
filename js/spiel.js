// wait for dom to load (just in case :p)
document.addEventListener('DOMContentLoaded', function() {
    let previousGameData = null;
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
        } catch (error) {
            console.error('Fehler beim Laden des Spiels:', error);
        }
    }
    function getGameId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('gameId');
    }
    function updateGameDisplay(game) {
        const base = game;

        if (!base || !base.Player || base.Player.length === 0) {
            console.error('Invalid game data:', game);
            return;
        }

        // Function to handle invalid throws
        function handleInvalidThrow(throwData) {
            const throwValue = throwData.Number * throwData.Modifier;
            if (throwValue === 0) {
                //alert('Invalid throw: 0 points. This throw will not be recorded.');
                return false;
            }
            return true;
        }

        // Updating Player 1
        const player1 = base.Player[0];
        const player1Name = document.getElementById('player1Name');
        const player1Score = document.getElementById('score1');
        const player1ThrowsContainer = document.getElementById('player1Throws');

        player1Name.textContent = player1.Name;
        player1Score.textContent = player1.Score?.Score || 0;

        // Fill in the last 3 throws
        if (player1.LastThrows && player1.LastThrows.length > 0) {
            player1.LastThrows.slice(0, 3).forEach((throwData, index) => {
                if (handleInvalidThrow(throwData)) {
                    const throwElement = document.getElementById(`throw-0-${index + 1}`);
                    throwElement.textContent = `${throwData.Number * throwData.Modifier}`;
                }
            });
        } else {
            for (let i = 0; i < 3; i++) {
                const throwElement = document.getElementById(`throw-0-${index + 1}`);
                throwElement.textContent = '-';
            }
        }

        // Updating Player 2 if exists
        if (base.Player.length > 1) {
            const player2 = base.Player[1];
            const player2Name = document.getElementById('player2Name');
            const player2Score = document.getElementById('score2');
            const player2ThrowsContainer = document.getElementById('player2Throws');

            player2Name.textContent = player2.Name;
            player2Score.textContent = player2.Score?.Score || 0;


            // Fill in the last 3 throws
            if (player2.LastThrows && player2.LastThrows.length > 0) {
                player2.LastThrows.slice(0, 3).forEach((throwData, index) => {
                    if (handleInvalidThrow(throwData)) {
                        const throwElement = document.getElementById(`throw-1-${index + 1}`);
                        throwElement.textContent = `${throwData.Number * throwData.Modifier}`;
                    }
                });
            } else {
                for (let i = 0; i < 3; i++) {
                    const throwElement = document.getElementById(`throw-1-${index + 1}`);
                    throwElement.textContent = '-';
                }
            }
        }

        const historyTableBody = document.getElementById('historyTableBody');
        if (historyTableBody) {
            historyTableBody.innerHTML = '';
            base.Player.forEach(player => {
                if (player.ThrowRounds) {
                    player.ThrowRounds.forEach(round => {
                        if (round.Throws && round.Throws.length > 0) {
                            const row = document.createElement('tr');
                            const playerNameCell = document.createElement('td');
                            const roundCell = document.createElement('td');
                            const pointsCell = document.createElement('td');

                            playerNameCell.textContent = player.Name;
                            roundCell.textContent = round.Round;
                            pointsCell.textContent = round.Throws.map(t => `${t.Number * t.Modifier}`).join(', ');

                            row.appendChild(playerNameCell);
                            row.appendChild(roundCell);
                            row.appendChild(pointsCell);
                            historyTableBody.appendChild(row);
                        }
                    });
                }
            });
        }

        previousGameData = game;
    }
    // nextPlayer: fetch game and nextPlayer, update last 3 throws, loadGame
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
        // get ActivePlayer
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
        console.log('ActivePlayer: ' + ActivePlayer);
        loadGame();
        clearLast3Throws(ActivePlayer);
    }

    function clearLast3Throws(player) {
        for (let i = 1; i <= 3; i++) {
            const throwElement = document.getElementById(`throw-${player}-${i}`);
            throwElement.innerHTML = '';
        }
    }

    /* game buttons */
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

            alert('Spiel erfolgreich beendet');
            window.location.href = 'index.html';
        } catch (error) {
            console.error('Fehler beim Beenden des Spiels:', error);
            alert('Fehler beim Beenden des Spiels: ' + error.message);
        }
    }
    const endGameButton = document.getElementById('end-game');
    endGameButton.addEventListener('click', endGame);
    
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
    

    window.onload = function() {
        loadGame();
        setInterval(loadGame, 5000); // Update every 5 seconds
    };
});