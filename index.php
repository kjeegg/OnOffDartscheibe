<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { background-color: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2); padding: 20px; animation: fadeIn 1s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    <title>Spielerregistrierung für Darts</title>
</head>
<body>
<div class="container mt-5">
    <h2 class="mb-3 text-center">Spielerregistrierung</h2>
    <form id="registrationForm">
        <div class="mb-3">
            <label for="playerName" class="form-label">Spielername</label>
            <input type="text" class="form-control" id="playerName" required>
        </div>
        <div class="mb-3">
            <label for="sessionNumber" class="form-label">Sitzungsnummer</label>
            <input type="number" class="form-control" id="sessionNumber" required>
        </div>
        <div class="d-grid gap-2">
            <button type="submit" class="btn btn-primary btn-lg">Registrieren</button>
        </div>
    </form>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
