// wait for dom to load (just in case :p)
document.addEventListener('DOMContentLoaded', function() {
    let previousGameData = null;
    async function loadGame() {
        const urlParams = new URLSearchParams(window.location.search);
        const gameId = urlParams.get('gameId');

        try {
            const response = await fetch(`https://api.dascr.local/api/game/${gameId}/display`, {
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

        // Remove existing throw elements
        while (player1ThrowsContainer.firstChild) {
            player1ThrowsContainer.removeChild(player1ThrowsContainer.firstChild);
        }

        // Create new throw elements from LastThrowsds
        if (player1.LastThrows && player1.LastThrows.length > 0) {
            player1.LastThrows.slice(0, 3).forEach((throwData, index) => {
                if (handleInvalidThrow(throwData)) {
                    const throwElement = document.createElement('div');
                    throwElement.className = `throw ${index + 1}-throw`;
                    throwElement.textContent = `${throwData.Number * throwData.Modifier}`;
                    player1ThrowsContainer.appendChild(throwElement);
                }
            });
        } else {
            for (let i = 0; i < 3; i++) {
                const throwElement = document.createElement('div');
                throwElement.className = `throw ${i + 1}-throw`;
                throwElement.textContent = 'No throws available';
                player1ThrowsContainer.appendChild(throwElement);
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

            // Remove existing throw elements
            while (player2ThrowsContainer.firstChild) {
                player2ThrowsContainer.removeChild(player2ThrowsContainer.firstChild);
            }

            // Create new throw elements from LastThrows
            if (player2.LastThrows && player2.LastThrows.length > 0) {
                player2.LastThrows.slice(0, 3).forEach((throwData, index) => {
                    if (handleInvalidThrow(throwData)) {
                        const throwElement = document.createElement('div');
                        throwElement.className = `throw ${index + 1}-throw`;
                        throwElement.textContent = `${throwData.Number * throwData.Modifier}`;
                        player2ThrowsContainer.appendChild(throwElement);
                    }
                });
            } else {
                for (let i = 0; i < 3; i++) {
                    const throwElement = document.createElement('div');
                    throwElement.className = `throw ${i + 1}-throw`;
                    throwElement.textContent = 'No throws available';
                    player2ThrowsContainer.appendChild(throwElement);
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

    /* game buttons */
    async function skipTurn() {
        console.log('Turn skipped');
        alert('Turn skipped');
    }
    const skipButton = document.getElementById('skip-turn');
    skipButton.addEventListener('click', skipTurn);

    async function manualEntry() {
        const points = prompt('Bitte geben Sie die Punkte ein:');
        if (points !== null) {
            console.log('Manual entry:', points);
            alert('Punkte manuell eingetragen: ' + points);
        }
    }
    const manualEntryButton = document.getElementById('manual-entry');
    manualEntryButton.addEventListener('click', manualEntry);

    async function endGame() {
        const urlParams = new URLSearchParams(window.location.search);
        const gameId = urlParams.get('gameId');

        try {
            const response = await fetch(`https://api.dascr.local/api/game/${gameId}`, {
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
    
    window.onload = function() {
        loadGame();
        setInterval(loadGame, 5000); // Update every 5 seconds
    };
    
    function getPlayerTurn(game) {
        const base = game.Base;
        const player1 = base.Player[0];
        const player2 = base.Player[1];

        if (player1.LastThrows % 3 === 0 && player1.Score !== 0) {
            return 1;
        }
        if (player2.LastThrows % 3 === 0 && player2.Score !== 0) {
            return 2;
        }
    }
    function updatePlayerTurn(game) {
        if(getPlayerTurn(game) === 1) {
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
    function manualPlayerTurn() {
        document.getElementById('player1-box').classList.toggle('active');
        document.getElementById('player2-box').classList.toggle('active');
        document.getElementById('arrow-wrapper').classList.toggle('active');
    }
    document.getElementById('arrow-wrapper').addEventListener('click', manualPlayerTurn);
});