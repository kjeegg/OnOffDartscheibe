<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Registrierung für Darts-Spieler</title>
</head>
<body>
<div class="container mt-5">
    <h2>Registrierung als Spieler</h2>
    <form id="registrationForm">
        <div class="mb-3">
            <label for="playerName" class="form-label">Spielername</label>
            <input type="text" class="form-control" id="playerName" required>
        </div>
        <div class="mb-3">
            <button type="submit" class="btn btn-primary">Registrieren</button>
        </div>
    </form>
</div>

<!-- Футер с ссылками на правовую информацию -->
<footer class="footer mt-auto py-3 bg-light fixed-bottom">
    <div class="container text-center">
            <span class="text-muted">
                Besuchen Sie unsere
                <a href="/impressum">Impressum</a> und
                <a href="/datenschutz">Datenschutzrichtlinie</a> Seiten für rechtliche Informationen.
            </span>
    </div>
</footer>

<!-- Баннер согласия на использование cookies -->
<div id="cookieConsent" class="alert alert-info fixed-bottom mb-0 text-center" style="display: none;">
    Diese Website verwendet Cookies, um die Benutzererfahrung zu verbessern.
    <a href="/datenschutz" class="alert-link">Datenschutzrichtlinie</a>.
    <button type="button" class="btn btn-success btn-sm" onclick="acceptCookies()">Einverstanden</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
    document.getElementById('registrationForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const playerName = document.getElementById('playerName').value;

        try {
            const response = await fetch('https://yourserver.com/api/player', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: playerName })
            });
            const data = await response.json();
            if (response.ok) {
                alert('Spieler erfolgreich registriert!');
            } else {
                alert('Fehler: ' + data.message);
            }
        } catch (error) {
            console.error('Fehler beim Registrieren:', error);
            alert('Netzwerkfehler beim Registrieren!');
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
</script>
</body>
</html>
