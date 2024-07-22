async function getHighestGameUID() {
    try {
        const response = await fetch('api.php?apiFunction=getHighestGameUID', {
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
        if (games !== null) {
            games.forEach(game => {
                if (game.uid > highestUID) {
                    highestUID = game.uid;
                }
            });
        }
        return highestUID;
    } catch (error) {
        console.error('Fehler beim Laden der Spiele:', error);
        alert('Fehler beim Laden der Spiele: ' + error.message);
        return null;
    }
}
// wait for dom to load
document.addEventListener('DOMContentLoaded', function() {
    // On click of the "Spielen" button, go to the game with the highest UID
    document.getElementById('playNavButton').addEventListener('click', async function(event) {
        event.preventDefault();
        const highestUID = await getHighestGameUID();

        // should not happen, highestUID is 0 if no games exist
        if (highestUID === null) {
            window.location.href = 'index.html';
        }

        window.location.href = 'spiel.html?gameId=' + highestUID;
    });
});
