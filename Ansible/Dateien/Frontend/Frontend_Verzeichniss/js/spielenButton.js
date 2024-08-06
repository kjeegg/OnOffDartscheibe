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

// On click of the "Spielen" button, go to the newest game (highest UID)
document.addEventListener('DOMContentLoaded', function() {
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
