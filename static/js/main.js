/* ==========================================================================
   EduTech AI - Zen Mode Interactive Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Determine current view context
    const isLearnView = document.querySelector('.zen-layout') !== null;
    const isFocusRoom = document.querySelector('.focus-room-layout') !== null;

    if (isLearnView) {
        initZenMode();
    } else if (isFocusRoom) {
        // Focus Room only needs Pomodoro + LoFi (no AI tabs or playlist toggles)
        initPomodoroTimer();
        initLofiPlayer();
    }

    // Auto-dismiss alert notifications
    initAlerts();
});

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

/**
 * Zen Mode Learner Dashboard Controllers
 */
function initZenMode() {
    // 1. Pomodoro Timer
    initPomodoroTimer();

    // 2. Lo-Fi Audio Player
    initLofiPlayer();

    // 3. AI Tab Control & Interactive Quiz Option Checking
    initAISection();

    // 4. Checklist Completion Toggle (AJAX)
    initPlaylistItemToggles();
}

/**
 * Pomodoro Timer Controller
 */
function initPomodoroTimer() {
    const timeDisplay = document.getElementById('pomodoro-time');
    const statusText = document.getElementById('pomodoro-status');
    const startBtn = document.getElementById('pomodoro-start');
    const resetBtn = document.getElementById('pomodoro-reset');
    const progressCircle = document.getElementById('pomodoro-progress');
    const presetBtns = document.querySelectorAll('.pomodoro-preset-btn');

    if (!timeDisplay || !startBtn || !progressCircle) return;

    let timerId = null;
    let totalSeconds = 25 * 60; // Default 25 minutes
    let remainingSeconds = totalSeconds;
    let isRunning = false;
    let currentMode = 'study'; // study, short, long

    const circlePerimeter = 477.5; // Stroke perimeter for r=76 (2 * PI * 76 = 477.52)

    function updateDisplay() {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Update circular svg path offset
        const percentage = remainingSeconds / totalSeconds;
        const offset = circlePerimeter * (1 - percentage);
        progressCircle.style.strokeDashoffset = offset;
    }

    function logStudySession(minutes) {
        const courseId = document.getElementById('course-meta-data').dataset.courseId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/course/${courseId}/log-session/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `duration_minutes=${minutes}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showToast(`Session recorded! Study streak: ${data.streak} days.`, 'success');
                    // Optional: Update dashboard metrics if streak incremented
                }
            })
            .catch(err => console.error("Error saving study session:", err));
    }

    function timerTick() {
        if (remainingSeconds <= 0) {
            clearInterval(timerId);
            timerId = null;
            isRunning = false;
            startBtn.innerHTML = '<span class="play-icon">▶</span> Start';

            // Audio alert notification
            playTimerAlarm();

            if (currentMode === 'study') {
                const minutesStudied = Math.round(totalSeconds / 60);
                showToast(`Focus time complete! +${minutesStudied} XP. Take a short rest.`, 'success');
                logStudySession(minutesStudied);
                switchMode('short', 5 * 60);
            } else {
                showToast("Break complete! Ready to lock back in?", 'success');
                switchMode('study', 25 * 60);
            }
            return;
        }
        remainingSeconds--;
        updateDisplay();
    }

    function playTimerAlarm() {
        const context = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = context.createOscillator();
        const gainNode = context.createGain();

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, context.currentTime); // A5 note
        gainNode.gain.setValueAtTime(0.1, context.currentTime);

        oscillator.connect(gainNode);
        gainNode.connect(context.destination);

        oscillator.start();
        setTimeout(() => oscillator.stop(), 500);
    }

    function startTimer() {
        if (isRunning) {
            // Pause
            clearInterval(timerId);
            timerId = null;
            isRunning = false;
            startBtn.innerHTML = '<span class="play-icon">▶</span> Resume';
            statusText.textContent = "Paused";
        } else {
            // Start
            isRunning = true;
            timerId = setInterval(timerTick, 1000);
            startBtn.innerHTML = '<span class="pause-icon">⏸</span> Pause';
            statusText.textContent = currentMode === 'study' ? "Locking in..." : "Resting...";
        }
    }

    function resetTimer() {
        clearInterval(timerId);
        timerId = null;
        isRunning = false;
        remainingSeconds = totalSeconds;
        updateDisplay();
        startBtn.innerHTML = '<span class="play-icon">▶</span> Start';
        statusText.textContent = currentMode === 'study' ? "Ready to focus" : "On break";
    }

    function switchMode(mode, seconds) {
        currentMode = mode;
        totalSeconds = seconds;
        remainingSeconds = seconds;

        presetBtns.forEach(btn => {
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Progress bar stroke color based on mode
        if (mode === 'study') {
            progressCircle.style.stroke = 'var(--accent-primary)';
            statusText.textContent = "Ready to focus";
        } else {
            progressCircle.style.stroke = 'var(--accent-secondary)';
            statusText.textContent = "On break";
        }

        resetTimer();
    }

    startBtn.addEventListener('click', startTimer);
    resetBtn.addEventListener('click', resetTimer);

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.mode === 'custom') return; // Handled separately
            const mode = btn.dataset.mode;
            const minutes = parseInt(btn.dataset.minutes);
            switchMode(mode, minutes * 60);
        });
    });

    // Custom Timer Panel Logic
    const customToggle = document.getElementById('custom-timer-toggle');
    const customPanel = document.getElementById('custom-timer-panel');
    const applyCustomBtn = document.getElementById('apply-custom-timer');
    const customHoursInput = document.getElementById('custom-hours');
    const customMinutesInput = document.getElementById('custom-minutes');

    if (customToggle && customPanel && applyCustomBtn) {
        customToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            customPanel.style.display = customPanel.style.display === 'none' ? 'block' : 'none';
            presetBtns.forEach(b => b.classList.remove('active'));
            customToggle.classList.add('active');
        });

        applyCustomBtn.addEventListener('click', () => {
            const hrs = parseInt(customHoursInput.value) || 0;
            const mins = parseInt(customMinutesInput.value) || 0;
            const totalSecs = (hrs * 3600) + (mins * 60);

            if (totalSecs <= 0) {
                showToast("Please enter a duration greater than 0.", "error");
                return;
            }

            customPanel.style.display = 'none';
            switchMode('custom', totalSecs);
            statusText.textContent = `Custom Focus (${hrs}h ${mins}m)`;
        });
    }

    // Initial display draw
    updateDisplay();
}

/**
 * Lo-Fi Concentration Music Player Controller
 */
function initLofiPlayer() {
    const lofiContainer = document.querySelector('.lofi-player');
    const audioSelect = document.getElementById('lofi-select');
    const playBtn = document.getElementById('lofi-play');
    const volumeSlider = document.getElementById('lofi-volume');

    if (!lofiContainer || !playBtn || !audioSelect) return;

    const audio = new Audio();
    audio.loop = true;
    let isPlaying = false;

    // Premium commercial-free 24/7 relaxing lofi and chillhop continuous streams
    const audioUrls = {
        'lofi': 'https://streams.ilovemusic.de/iloveradio17.mp3',
        'chillout': 'https://streams.ilovemusic.de/iloveradio14.mp3',
        'lounge': 'https://streams.ilovemusic.de/iloveradio10.mp3',
        'zeno': 'https://stream.zeno.fm/f3wvbbqmdg8uv'
    };

    function loadTrack() {
        const selected = audioSelect.value;
        const url = audioUrls[selected];
        if (url) {
            audio.src = url;
            audio.load();
        }
    }

    function togglePlay() {
        if (!audio.src) {
            loadTrack();
        }

        if (isPlaying) {
            audio.pause();
            isPlaying = false;
            playBtn.innerHTML = '▶';
            lofiContainer.classList.remove('playing');
        } else {
            audio.play().then(() => {
                isPlaying = true;
                playBtn.innerHTML = '⏸';
                lofiContainer.classList.add('playing');
            }).catch(err => {
                console.error("Audio playback error:", err);
                showToast("Could not stream sound. Please try another.", "error");
            });
        }
    }

    playBtn.addEventListener('click', togglePlay);
    audioSelect.addEventListener('change', () => {
        const wasPlaying = isPlaying;
        if (wasPlaying) {
            audio.pause();
        }
        loadTrack();
        if (wasPlaying) {
            audio.play().then(() => {
                lofiContainer.classList.add('playing');
            });
        }
    });

    volumeSlider.addEventListener('input', (e) => {
        audio.volume = e.target.value;
    });

    // Initialize volume from slider value
    audio.volume = volumeSlider.value;
}

/**
 * AI Study Buddy Tabs & Quiz Option Checker
 */
function initAISection() {
    const tabBtns = document.querySelectorAll('.ai-tab-btn');
    const contentPanels = document.querySelectorAll('.ai-content-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            contentPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`ai-panel-${target}`).classList.add('active');
        });
    });

    // Interactive Multiple-Choice Quiz click events
    const quizOptions = document.querySelectorAll('.quiz-option-btn');
    quizOptions.forEach(btn => {
        btn.addEventListener('click', function () {
            const isCorrect = this.dataset.correct === "true";
            const siblings = this.parentElement.querySelectorAll('.quiz-option-btn');

            // Disable further clicks for this question once answered
            siblings.forEach(sib => sib.disabled = true);

            if (isCorrect) {
                this.classList.add('correct');
                this.innerHTML += ' ✓';
                showToast("Spot on! Correct answer.", "success");
            } else {
                this.classList.add('incorrect');
                this.innerHTML += ' ✗';

                // Highlight the correct sibling
                siblings.forEach(sib => {
                    if (sib.dataset.correct === "true") {
                        sib.classList.add('correct');
                        sib.innerHTML += ' ✓';
                    }
                });
                showToast("Not quite. Keep studying!", "error");
            }
        });
    });
}

/**
 * Curriculum Checklist completeness toggling
 */
function initPlaylistItemToggles() {
    // Manual checkbox toggling is removed.
    // Video completion is automatically managed via YouTube player state transitions (status-dot).
}

/**
 * Show premium toast alert notifications
 */
function showToast(message, type = 'success') {
    let container = document.querySelector('.messages-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'messages-container';
        document.body.appendChild(container);
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <span class="close-alert" style="cursor:pointer; margin-left:1.5rem; font-weight:700;">&times;</span>
    `;

    container.appendChild(alert);

    // Close alert on click
    alert.querySelector('.close-alert').addEventListener('click', () => alert.remove());

    // Auto remove after 4 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => alert.remove(), 400);
    }, 4000);
}
