// no idea if this works
async function loadTopPlayers() {
    try {
        const response = await fetch('https://api.dascr.local/api/player', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        // sort players by score
        const players = await response.json();
        players.sort((a, b) => b.Score - a.Score);

        // display top 10 players
        const leaderboard = document.getElementById('leaderboard');
        leaderboard.innerHTML = '';
        for (let i = 0; i < 10 && i < players.length; i++) {
            const player = players[i];
            const playerElement = document.createElement('tr');
            playerElement.className = 'player';
            playerElement.innerHTML = `<td class="number">${i}</td> <td class="name">${player.Name}</td> <td class="score">${player.Score}</td>`;
            leaderboard.appendChild(playerElement);
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
}
document.addEventListener('DOMContentLoaded', function() {
    loadTopPlayers();
});