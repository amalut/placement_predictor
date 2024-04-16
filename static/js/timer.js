const countdownTime = 1500;
        let timeLeft = countdownTime;

        // Function to format time as minutes and seconds
        function formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
        }

        // Function to update the timer display and submit the form when time runs out
        function updateTimer() {
            // Update the timer display
            const timerDisplay = document.getElementById('time');
            timerDisplay.textContent = formatTime(timeLeft);

            // Check if time has run out
            if (timeLeft <= 0) {
                // Submit the form automatically
                document.getElementById('quizForm').submit();
            } else {
                // Decrement the time left and call this function again after 1 second
                timeLeft--;
                setTimeout(updateTimer, 1000);
            }
        }

        // Start the countdown timer
        updateTimer();