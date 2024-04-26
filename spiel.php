<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { background-color: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2); padding: 20px; }
        .darts-image {
            width: 100%;
            height: auto;
            border-radius: 5px;
        }
    </style>
    <title>Dartspiel</title>
</head>
<body>
<div class="container mt-5">
    <h2 class="mb-4 text-center">Spielertabelle</h2>
    <table class="table">
        <thead class="table-dark">
        <tr>
            <th scope="col">Name</th>
            <th scope="col">Punktestand</th>
        </tr>
        </thead>
        <tbody>
        <!-- Tabelle von spieler -->
        </tbody>
    </table>

    <div class="row">
        <div class="col-md-8">
            <h3>Dartscheibe</h3>
            <!-- Interaktive Dartscheibe -->
            <div id="dartboard" style="height: 600px; background: url('https://cdn.pixabay.com/photo/2016/08/23/10/48/dart-board-1614051_1280.png') center/cover no-repeat;"></div>
        </div>
        <div class="col-md-4">
            <h3>Persönliche Statistik</h3>
            <canvas id="statsChart"></canvas>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Chart.js-Code für die Statistik
    const ctx = document.getElementById('statsChart').getContext('2d');
    const statsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Spiel 1', 'Spiel 2', 'Spiel 3'],
            datasets: [{
                label: 'Punkte pro Spiel',
                data: [12, 19, 3],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Verarbeiter für Klicks auf die Dartscheibe
    document.getElementById('dartboard').addEventListener('click', function(e) {
        // Hier können die Koordinaten des Klicks verarbeitet werden
        console.log('Clicked on dartboard at coordinates:', e.clientX, e.clientY);
    });
</script>
</body>
</html>
