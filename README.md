# OnOff Dartboard Project

## What is the OnOff Dartboard Project?

This project is an innovative system that brings a digital experience to the traditional game of darts. It connects a physical dartboard to a computer and a web interface, allowing players to track scores automatically, manage games, and view leaderboards through a modern digital platform.

Think of it as a smart dartboard system that makes playing darts more interactive and engaging by combining the physical game with digital technology.

## What Does it Do?

The OnOff Dartboard system automates the scoring process for dart games. When a dart hits the board, sensors detect the score, and this information is sent to a central system. Players and spectators can then see the scores updated in real-time on a web page accessible from computers or mobile devices on the same network.

Key functions include:

*   **Automatic Scoring:** No need for manual scorekeeping.
*   **Game Management:** Start, manage, and end dart games digitally.
*   **Real-time Display:** Scores and game information are shown instantly on a web interface and potentially on a small screen near the dartboard.
*   **Leaderboards:** Keep track of high scores and player rankings.
*   **Interactive Elements:** The system can control lights (LEDs) and potentially use cameras or lasers for enhanced interaction.

## How Does it Work (Simply Explained)?

The system has a few main parts that work together:

1.  **The Smart Dartboard:** A regular dartboard is enhanced with sensors to detect where darts land.
2.  **Small Computers (Raspberry Pis):** These small computers are connected to the dartboard's sensors, a small display screen, and lights. They read the sensor data, figure out the score, control the display and lights, and send the score information wirelessly.
3.  **Central Computer (Server):** A computer (like a regular PC) runs software that receives scores from the Raspberry Pis and keeps track of the game state, players, and leaderboards. This software also hosts the web page.
4.  **Web Page (Frontend):** This is what players and users see in their web browser. It shows the current scores, game status, and leaderboards. It communicates with the central computer.

When a dart hits the board, a Raspberry Pi detects it, sends the score to the central computer, which updates the game data, and the web page automatically refreshes to show the new score.

## Why is it Useful?

This project modernizes the dart game experience. It eliminates scoring disputes, makes games more dynamic with visual feedback (lights, display), and adds a competitive element with digital leaderboards. It's a great example of how technology can enhance traditional activities.

## Project Components (High-Level):

*   **Hardware:** Physical dartboard, sensors, Raspberry Pi computers, small LCD screens, LED lights.
*   **Software:**
    *   Python scripts running on the Raspberry Pis to interact with the hardware.\n    *   Web server software (using Docker) running on a central computer.
    *   Web pages (HTML, CSS, JavaScript) for the user interface.
    *   A simple backend script (PHP) to handle data between the web page and the Raspberry Pis.

## Getting Started (For Technical Users):

This project requires setting up both the hardware (Raspberry Pis connected to the dartboard) and the software (Docker on a PC). Detailed instructions for a local setup are included within the project files, specifically in the original README (in German) and the scripts in the `Docker` and `PIs` folders.
