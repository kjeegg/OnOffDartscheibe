// Get all games and calculate the average points
async function getGames() {
    try {
        const response = await fetch('api.php?apiFunction=getAllGames', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const games = await response.json();

        let allAverages = [];

        // get all players and their average points per round
        //* players are stored multiple times in the array, once for each game they played
        games.forEach(game => {
            game.GameObject.Base.Player.forEach(player => {
                allAverages.push({
                    uid: player.UID,
                    name: player.Name,
                    average: player.Average
                });
            });
        });

        // get average points per round across all games
        //* each player is only stored once
        let playerAverages = [];
        allAverages.forEach(player => {
            let existingPlayer = playerAverages.find(p => p.uid === player.uid);
            if (existingPlayer) {
                existingPlayer.average += player.average;
                existingPlayer.count++;
            } else {
                playerAverages.push({
                    uid: player.uid,
                    name: player.name,
                    average: player.average,
                    count: 1
                });
            }
        });

        playerAverages.forEach(player => {
            player.average /= player.count;
        });

        playerAverages.sort((a, b) => b.average - a.average);

        displayLeaderboard(playerAverages);
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

function displayLeaderboard(playerAverages) {
    const leaderboard = document.getElementById('leaderboard');
    leaderboard.innerHTML = '';

    playerAverages.forEach((player, i) => {
        // console.log(`${i + 1}. ${player.name} - Average Points per Round: ${player.average.toFixed(2)}`);
        const playerElement = document.createElement('tr');
        playerElement.className = 'player';
        playerElement.innerHTML = `<td class="number">${i+1}</td> <td class="name">${player.name}</td> <td class="uid">${player.uid}</td> <td class="score">${player.average.toFixed(2)}</td>`;
        leaderboard.appendChild(playerElement);
    });
  }
document.addEventListener('DOMContentLoaded', function() {
    getGames();
});