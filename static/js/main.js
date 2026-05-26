/* ==========================================================================
   EduTech AI - Zen Mode Interactive Logic
   ========================================================================== */

/* ==========================================================================
   THEME TRANSITION SYSTEM — Curtain Rise / Curtain Fall
   Orchestrates the magical switch between light (logged in) and dark (logged out)
   ========================================================================== */

(function initThemeSystem() {
    const html = document.documentElement;
    const lightCurtain = document.getElementById('light-curtain');
    const darkCurtain = document.getElementById('dark-curtain');
    const transitionIcon = document.getElementById('theme-transition-icon');
    const iconSun = document.getElementById('theme-icon-sun');
    const iconMoon = document.getElementById('theme-icon-moon');

    // Determine correct theme from the server-rendered data-theme attribute
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    window.__THEME_STATE__ = currentTheme;

    /**
     * Perform a curtain-based theme switch.
     * @param {'light'|'dark'} targetTheme
     */
    window.switchTheme = function (targetTheme) {
        if (window.__THEME_STATE__ === targetTheme) return;
        const prevTheme = window.__THEME_STATE__;
        window.__THEME_STATE__ = targetTheme;
        window.__THEME_SWITCHING__ = true;

        // Show the appropriate curtain
        const curtain = targetTheme === 'light' ? lightCurtain : darkCurtain;
        const icon = targetTheme === 'light' ? iconSun : iconMoon;

        // Show curtain (curtain rises / falls over the screen)
        if (curtain) {
            curtain.classList.remove('closing');
            curtain.classList.add('active');
        }

        // Show transition icon
        if (transitionIcon && icon) {
            iconSun.style.display = targetTheme === 'light' ? 'block' : 'none';
            iconMoon.style.display = targetTheme === 'dark' ? 'block' : 'none';
            transitionIcon.classList.add('show');
        }

        // Switch the data-theme attribute mid-curtain (at peak coverage)
        setTimeout(() => {
            html.classList.add('theme-transitioning');
            html.setAttribute('data-theme', targetTheme);
            localStorage.setItem('eduThemeMode', targetTheme);

            // Animate transition icon out
            if (transitionIcon) {
                transitionIcon.classList.remove('show');
            }

            // Begin closing the curtain (reveal the new theme beneath)
            if (curtain) {
                curtain.classList.add('closing');
                curtain.classList.remove('active');
            }

            // Dispatch event for other components to react
            window.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: targetTheme, previous: prevTheme }
            }));

            // Clean up after animations complete
            setTimeout(() => {
                if (curtain) {
                    curtain.classList.remove('closing');
                }
                html.classList.remove('theme-transitioning');
                window.__THEME_SWITCHING__ = false;

                // Re-initialize WebGL backgrounds if present
                if (window.__lightRaysInstance__ && window.__lightRaysInstance__.updateOptions) {
                    window.__lightRaysInstance__.updateOptions({
                        theme: targetTheme
                    });
                }
            }, 600);
        }, 350);
    };

    /**
     * Watch for auth state changes (login/logout) via page transitions.
     * The server sets data-theme on initial render; JS handles SPA-like transitions.
     */
    // Expose current state for other scripts
    window.getCurrentTheme = function () { return window.__THEME_STATE__; };
    window.isThemeSwitching = function () { return !!window.__THEME_SWITCHING__; };

    // If the page loads with light theme, ensure smooth initial state
    if (currentTheme === 'light') {
        html.classList.add('theme-transitioning');
        requestAnimationFrame(() => {
            // Small delay to let CSS catch up, then remove transition class
            setTimeout(() => {
                html.classList.remove('theme-transitioning');
            }, 100);
        });
    }

    console.log(`[ThemeSystem] Initialized with theme: ${currentTheme}`);
})();

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

    // Scroll-triggered reveal animations (About page)
    initScrollReveal();

    // Timeline node pulse animation on scroll
    initTimelinePulse();

    // Count-up animations for statistics
    initCountUpAnimation();
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
/**
 * Pomodoro Timer
 */
function initPomodoroTimer() {
    // Pomodoro logic
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

(function () {

    // Mesmerizing High-Performance WebGL2 Plasma Engine Class
    class Plasma {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.getElementById(container) : container;
            if (!this.container) return;

            this.color = options.color || '#ffffff';
            this.speed = options.speed !== undefined ? options.speed : 1.0;
            this.direction = options.direction || 'forward';
            this.scale = options.scale !== undefined ? options.scale : 1.0;
            this.opacity = options.opacity !== undefined ? options.opacity : 1.0;
            this.mouseInteractive = options.mouseInteractive !== undefined ? options.mouseInteractive : true;

            this.canvas = null;
            this.gl = null;
            this.program = null;
            this.animationId = null;

            this.mouse = { x: 0, y: 0 };
            this.targetMouse = { x: 0, y: 0 };

            this.t0 = performance.now();
            this.isPaused = false;

            this.init();
        }

        init() {
            this.canvas = document.createElement('canvas');
            this.canvas.style.display = 'block';
            this.canvas.style.width = '100%';
            this.canvas.style.height = '100%';
            this.container.appendChild(this.canvas);

            const glOpts = {
                alpha: true,
                antialias: false,
                depth: false,
                stencil: false,
                powerPreference: "high-performance"
            };
            this.gl = this.canvas.getContext('webgl2', glOpts);
            if (!this.gl) {
                console.error("WebGL2 not supported in this browser.");
                return;
            }

            const vertexShaderSource = `#version 300 es
            precision highp float;
            in vec2 position;
            out vec2 vUv;
            void main() {
                vUv = position * 0.5 + 0.5;
                gl_Position = vec4(position, 0.0, 1.0);
            }`;

            const fragmentShaderSource = `#version 300 es
            precision highp float;
            uniform vec2 iResolution;
            uniform float iTime;
            uniform vec3 uCustomColor;
            uniform float uUseCustomColor;
            uniform float uSpeed;
            uniform float uDirection;
            uniform float uScale;
            uniform float uOpacity;
            uniform vec2 uMouse;
            uniform float uMouseInteractive;
            out vec4 fragColor;

            void mainImage(out vec4 o, vec2 C) {
                vec2 center = iResolution.xy * 0.5;
                C = (C - center) / uScale + center;
                
                vec2 mouseOffset = (uMouse - center) * 0.0002;
                C += mouseOffset * length(C - center) * step(0.5, uMouseInteractive);
                
                float i = 0.0;
                float d = 0.0;
                float z = 0.0;
                float T = iTime * uSpeed * uDirection;
                vec3 O = vec3(0.0);
                vec3 p = vec3(0.0);
                vec3 S = vec3(0.0);
                vec2 r = iResolution.xy;
                vec2 Q = vec2(0.0);
                
                for (int idx = 0; idx < 60; idx++) {
                    i += 1.0;
                    p = z * normalize(vec3(C - 0.5 * r, r.y)); 
                    p.z -= 4.0; 
                    S = p;
                    d = p.y - T;
                    
                    p.x += 0.4 * (1.0 + p.y) * sin(d + p.x * 0.1) * cos(0.34 * d + p.x * 0.05); 
                    
                    vec4 mVec = cos(p.y + vec4(0.0, 11.0, 33.0, 0.0) - T);
                    mat2 m = mat2(mVec.x, mVec.y, mVec.z, mVec.w);
                    p.xz = p.xz * m;
                    Q = p.xz;
                    
                    d = abs(sqrt(length(Q * Q)) - 0.25 * (5.0 + S.y)) / 3.0 + 8.0e-4; 
                    z += d; 
                    
                    o = 1.0 + sin(S.y + p.z * 0.5 + S.z - length(S - p) + vec4(2.0, 1.0, 0.0, 8.0));
                    O += o.w / d * o.xyz;
                }
                
                o.xyz = tanh(O / 1e4);
            }

            bool finite1(float x) { return !(isnan(x) || isinf(x)); }
            vec3 sanitize(vec3 c) {
                return vec3(
                    finite1(c.r) ? c.r : 0.0,
                    finite1(c.g) ? c.g : 0.0,
                    finite1(c.b) ? c.b : 0.0
                );
            }

            void main() {
                vec4 o = vec4(0.0);
                mainImage(o, gl_FragCoord.xy);
                vec3 rgb = sanitize(o.rgb);
                
                float intensity = (rgb.r + rgb.g + rgb.b) / 3.0;
                vec3 customColor = intensity * uCustomColor;
                vec3 finalColor = mix(rgb, customColor, step(0.5, uUseCustomColor));
                
                float alpha = length(rgb) * uOpacity;
                fragColor = vec4(finalColor, alpha);
            }`;

            // Compile shaders and program
            const vs = this.gl.createShader(this.gl.VERTEX_SHADER);
            this.gl.shaderSource(vs, vertexShaderSource);
            this.gl.compileShader(vs);
            if (!this.gl.getShaderParameter(vs, this.gl.COMPILE_STATUS)) {
                console.error("VS Compile Error:", this.gl.getShaderInfoLog(vs));
                return;
            }

            const fs = this.gl.createShader(this.gl.FRAGMENT_SHADER);
            this.gl.shaderSource(fs, fragmentShaderSource);
            this.gl.compileShader(fs);
            if (!this.gl.getShaderParameter(fs, this.gl.COMPILE_STATUS)) {
                console.error("FS Compile Error:", this.gl.getShaderInfoLog(fs));
                return;
            }

            this.program = this.gl.createProgram();
            this.gl.attachShader(this.program, vs);
            this.gl.attachShader(this.program, fs);
            this.gl.linkProgram(this.program);
            if (!this.gl.getShaderParameter(this.program, this.gl.LINK_STATUS)) {
                console.error("Link Error:", this.gl.getProgramInfoLog(this.program));
                return;
            }

            this.gl.useProgram(this.program);

            // Full-screen triangle buffer setup
            const positions = new Float32Array([
                -1.0, -1.0,
                3.0, -1.0,
                -1.0, 3.0
            ]);

            const vao = this.gl.createVertexArray();
            this.gl.bindVertexArray(vao);

            const buffer = this.gl.createBuffer();
            this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
            this.gl.bufferData(this.gl.ARRAY_BUFFER, positions, this.gl.STATIC_DRAW);

            const posLoc = this.gl.getAttribLocation(this.program, 'position');
            this.gl.enableVertexAttribArray(posLoc);
            this.gl.vertexAttribPointer(posLoc, 2, this.gl.FLOAT, false, 0, 0);

            // Get Uniform Locations
            this.uniforms = {
                iTime: this.gl.getUniformLocation(this.program, 'iTime'),
                iResolution: this.gl.getUniformLocation(this.program, 'iResolution'),
                uCustomColor: this.gl.getUniformLocation(this.program, 'uCustomColor'),
                uUseCustomColor: this.gl.getUniformLocation(this.program, 'uUseCustomColor'),
                uSpeed: this.gl.getUniformLocation(this.program, 'uSpeed'),
                uDirection: this.gl.getUniformLocation(this.program, 'uDirection'),
                uScale: this.gl.getUniformLocation(this.program, 'uScale'),
                uOpacity: this.gl.getUniformLocation(this.program, 'uOpacity'),
                uMouse: this.gl.getUniformLocation(this.program, 'uMouse'),
                uMouseInteractive: this.gl.getUniformLocation(this.program, 'uMouseInteractive')
            };

            // Bind Event Listeners
            this._onResize = this.onResize.bind(this);
            window.addEventListener('resize', this._onResize);

            // Modern ResizeObserver to handle layout rendering delays robustly
            if (window.ResizeObserver) {
                this.resizeObserver = new ResizeObserver(() => this.onResize());
                this.resizeObserver.observe(this.container);
            }

            this.onResize();

            // Set static / initial uniforms
            const hexToRgb = (hex) => {
                const res = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                if (!res) return [1.0, 0.5, 0.2];
                return [
                    parseInt(res[1], 16) / 255,
                    parseInt(res[2], 16) / 255,
                    parseInt(res[3], 16) / 255
                ];
            };

            const useCustomColor = this.color ? 1.0 : 0.0;
            const customColorRgb = this.color ? hexToRgb(this.color) : [1.0, 1.0, 1.0];
            const directionMultiplier = this.direction === 'reverse' ? -1.0 : 1.0;

            this.gl.uniform3fv(this.uniforms.uCustomColor, new Float32Array(customColorRgb));
            this.gl.uniform1f(this.uniforms.uUseCustomColor, useCustomColor);
            this.gl.uniform1f(this.uniforms.uSpeed, this.speed * 0.4);
            this.gl.uniform1f(this.uniforms.uDirection, directionMultiplier);
            this.gl.uniform1f(this.uniforms.uScale, this.scale);
            this.gl.uniform1f(this.uniforms.uOpacity, this.opacity);
            this.gl.uniform1f(this.uniforms.uMouseInteractive, this.mouseInteractive ? 1.0 : 0.0);

            if (this.mouseInteractive) {
                this._onMouseMove = this.onMouseMove.bind(this);
                window.addEventListener('mousemove', this._onMouseMove);
            }

            // Set initial mouse at center
            const rect = this.container.getBoundingClientRect();
            this.mouse.x = rect.width / 2;
            this.mouse.y = rect.height / 2;
            this.targetMouse.x = this.mouse.x;
            this.targetMouse.y = this.mouse.y;

            // Setup Intersection Observer to pause when off-screen
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    this.isPaused = !entry.isIntersecting;
                });
            }, { threshold: 0.1 });
            this.observer.observe(this.container);

            // Start animation loop
            this.loop(performance.now());
        }

        onMouseMove(e) {
            if (!this.mouseInteractive) return;
            const rect = this.container.getBoundingClientRect();
            this.targetMouse.x = e.clientX - rect.left;
            this.targetMouse.y = e.clientY - rect.top;
        }

        onResize() {
            if (!this.container || !this.canvas || !this.gl) return;
            const rect = this.container.getBoundingClientRect();
            const width = Math.max(1, Math.floor(rect.width));
            const height = Math.max(1, Math.floor(rect.height));

            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            this.canvas.width = width * dpr;
            this.canvas.height = height * dpr;

            this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
            this.gl.uniform2f(this.uniforms.iResolution, this.canvas.width, this.canvas.height);
        }

        loop(t) {
            this.animationId = requestAnimationFrame(this.loop.bind(this));

            if (this.isPaused) return;

            // Easing the mouse position
            this.mouse.x += (this.targetMouse.x - this.mouse.x) * 0.08;
            this.mouse.y += (this.targetMouse.y - this.mouse.y) * 0.08;

            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            const rect = this.container.getBoundingClientRect();
            const mouseX = this.mouse.x * dpr;
            const mouseY = (rect.height - this.mouse.y) * dpr;
            this.gl.uniform2f(this.uniforms.uMouse, mouseX, mouseY);

            let timeValue = (t - this.t0) * 0.001;
            if (this.direction === 'pingpong') {
                const pingpongDuration = 10;
                const segmentTime = timeValue % (pingpongDuration * 2);
                const pingpongTime = segmentTime > pingpongDuration
                    ? (pingpongDuration * 2 - segmentTime)
                    : segmentTime;
                this.gl.uniform1f(this.uniforms.iTime, pingpongTime);
            } else {
                this.gl.uniform1f(this.uniforms.iTime, timeValue);
            }

            this.gl.drawArrays(this.gl.TRIANGLES, 0, 3);
        }

        destroy() {
            if (this.animationId) cancelAnimationFrame(this.animationId);
            window.removeEventListener('resize', this._onResize);
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
            }
            if (this.mouseInteractive && this._onMouseMove) {
                window.removeEventListener('mousemove', this._onMouseMove);
            }
            if (this.observer) {
                this.observer.disconnect();
            }
            if (this.canvas && this.canvas.parentNode) {
                this.canvas.parentNode.removeChild(this.canvas);
            }
        }
    }

    class LightRays {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.getElementById(container) : container;
            if (!this.container) return;

            this.raysOrigin = options.raysOrigin || 'top-center';
            this.raysColor = options.raysColor || '#ffffff';
            this.raysSpeed = options.raysSpeed !== undefined ? options.raysSpeed : 1.0;
            this.lightSpread = options.lightSpread !== undefined ? options.lightSpread : 1.0;
            this.rayLength = options.rayLength !== undefined ? options.rayLength : 2.0;
            this.pulsating = options.pulsating !== undefined ? options.pulsating : false;
            this.fadeDistance = options.fadeDistance !== undefined ? options.fadeDistance : 1.0;
            this.saturation = options.saturation !== undefined ? options.saturation : 1.0;
            this.followMouse = options.followMouse !== undefined ? options.followMouse : true;
            this.mouseInfluence = options.mouseInfluence !== undefined ? options.mouseInfluence : 0.1;
            this.noiseAmount = options.noiseAmount !== undefined ? options.noiseAmount : 0.02;
            this.distortion = options.distortion !== undefined ? options.distortion : 0.05;

            this.canvas = null;
            this.gl = null;
            this.program = null;
            this.animationId = null;

            this.mouse = { x: 0.5, y: 0.5 };
            this.smoothMouse = { x: 0.5, y: 0.5 };

            this.t0 = performance.now();
            this.isPaused = false;

            this.init();
        }

        hexToRgb(hex) {
            const res = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            if (!res) return [1.0, 1.0, 1.0];
            return [
                parseInt(res[1], 16) / 255,
                parseInt(res[2], 16) / 255,
                parseInt(res[3], 16) / 255
            ];
        }

        getAnchorAndDir(origin, w, h) {
            const outside = 0.2;
            switch (origin) {
                case 'top-left':
                    return { anchor: [0, -outside * h], dir: [0.7, 0.7] };
                case 'top-right':
                    return { anchor: [w, -outside * h], dir: [-0.7, 0.7] };
                case 'left':
                    return { anchor: [-outside * w, 0.5 * h], dir: [1, 0] };
                case 'right':
                    return { anchor: [(1 + outside) * w, 0.5 * h], dir: [-1, 0] };
                case 'bottom-left':
                    return { anchor: [0, (1 + outside) * h], dir: [0.7, -0.7] };
                case 'bottom-center':
                    return { anchor: [0.5 * w, (1 + outside) * h], dir: [0, -1] };
                case 'bottom-right':
                    return { anchor: [w, (1 + outside) * h], dir: [-0.7, -0.7] };
                default: // "top-center"
                    return { anchor: [0.5 * w, -outside * h], dir: [0, 1] };
            }
        }

        init() {
            this.canvas = document.createElement('canvas');
            this.canvas.style.display = 'block';
            this.canvas.style.width = '100%';
            this.canvas.style.height = '100%';
            this.container.appendChild(this.canvas);

            const glOpts = {
                alpha: true,
                antialias: false,
                depth: false,
                stencil: false,
                powerPreference: "high-performance"
            };
            this.gl = this.canvas.getContext('webgl2', glOpts);
            if (!this.gl) {
                console.error("WebGL2 not supported in this browser.");
                return;
            }

            const vertexShaderSource = `#version 300 es
            precision highp float;
            in vec2 position;
            out vec2 vUv;
            void main() {
                vUv = position * 0.5 + 0.5;
                gl_Position = vec4(position, 0.0, 1.0);
            }`;

            const fragmentShaderSource = `#version 300 es
            precision highp float;
            uniform float iTime;
            uniform vec2  iResolution;
            uniform vec2  rayPos;
            uniform vec2  rayDir;
            uniform vec3  raysColor;
            uniform float raysSpeed;
            uniform float lightSpread;
            uniform float rayLength;
            uniform float pulsating;
            uniform float fadeDistance;
            uniform float saturation;
            uniform vec2  mousePos;
            uniform float mouseInfluence;
            uniform float noiseAmount;
            uniform float distortion;
            in vec2 vUv;
            out vec4 fragColor;

            float noise(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord,
                              float seedA, float seedB, float speed) {
                vec2 sourceToCoord = coord - raySource;
                vec2 dirNorm = normalize(sourceToCoord);
                float cosAngle = dot(dirNorm, rayRefDirection);
                
                float d = distortion * sin(iTime * 1.5 + length(sourceToCoord) * 0.005);
                float distortedAngle = cosAngle + d;
                
                float spreadFactor = pow(max(distortedAngle, 0.0), 1.0 / max(lightSpread, 0.001));
                float distance = length(sourceToCoord);
                float maxDistance = max(iResolution.x, iResolution.y) * rayLength;
                float lengthFalloff = clamp((maxDistance - distance) / maxDistance, 0.0, 1.0);
                
                float fadeFactor = fadeDistance * max(iResolution.x, iResolution.y);
                float fadeFalloff = clamp((fadeFactor - distance) / fadeFactor, 0.0, 1.0);
                
                float pulse = pulsating > 0.5 ? (0.85 + 0.15 * sin(iTime * speed * 4.0)) : 1.0;
                
                float baseStrength = clamp(
                    (0.5 + 0.2 * sin(distortedAngle * seedA + iTime * speed)) +
                    (0.3 + 0.2 * cos(-distortedAngle * seedB + iTime * speed * 0.8)),
                    0.0, 1.0
                );
                
                return baseStrength * lengthFalloff * fadeFalloff * spreadFactor * pulse;
            }

            void main() {
                vec2 fragCoord = gl_FragCoord.xy;
                vec2 coord = vec2(fragCoord.x, fragCoord.y);
                
                vec2 finalRayDir = normalize(rayDir);
                if (mouseInfluence > 0.0) {
                    vec2 mouseScreenPos = mousePos * iResolution.xy;
                    vec2 mouseDirection = normalize(mouseScreenPos - rayPos);
                    finalRayDir = normalize(mix(finalRayDir, mouseDirection, mouseInfluence));
                }

                float r1 = rayStrength(rayPos, finalRayDir, coord, 45.2, 31.4, 0.8 * raysSpeed);
                float r2 = rayStrength(rayPos, finalRayDir, coord, 28.5, 19.8, 1.2 * raysSpeed);
                float r3 = rayStrength(rayPos, finalRayDir, coord, 12.1, 56.2, 0.5 * raysSpeed);
                
                float combined = (r1 * 0.4 + r2 * 0.4 + r3 * 0.2);
                combined = pow(combined, 0.7);
                combined *= 1.5;
                vec3 finalColor = raysColor * combined;
                
                if (noiseAmount > 0.0) {
                    float n = noise(coord * 0.01 + iTime * 0.05);
                    finalColor *= (1.0 - noiseAmount + noiseAmount * n);
                }

                if (saturation != 1.0) {
                    float gray = dot(finalColor, vec3(0.299, 0.587, 0.114));
                    finalColor = mix(vec3(gray), finalColor, saturation);
                }

                fragColor = vec4(finalColor, combined);
            }`;

            // Compile shaders and program
            const vs = this.gl.createShader(this.gl.VERTEX_SHADER);
            this.gl.shaderSource(vs, vertexShaderSource);
            this.gl.compileShader(vs);
            if (!this.gl.getShaderParameter(vs, this.gl.COMPILE_STATUS)) {
                console.error("VS Compile Error:", this.gl.getShaderInfoLog(vs));
                return;
            }

            const fs = this.gl.createShader(this.gl.FRAGMENT_SHADER);
            this.gl.shaderSource(fs, fragmentShaderSource);
            this.gl.compileShader(fs);
            if (!this.gl.getShaderParameter(fs, this.gl.COMPILE_STATUS)) {
                console.error("FS Compile Error:", this.gl.getShaderInfoLog(fs));
                return;
            }

            this.program = this.gl.createProgram();
            this.gl.attachShader(this.program, vs);
            this.gl.attachShader(this.program, fs);
            this.gl.linkProgram(this.program);
            if (!this.gl.getShaderParameter(this.program, this.gl.LINK_STATUS)) {
                console.error("Link Error:", this.gl.getProgramInfoLog(this.program));
                return;
            }

            this.gl.useProgram(this.program);

            // Full-screen triangle buffer setup
            const positions = new Float32Array([
                -1.0, -1.0,
                3.0, -1.0,
                -1.0, 3.0
            ]);

            const vao = this.gl.createVertexArray();
            this.gl.bindVertexArray(vao);

            const buffer = this.gl.createBuffer();
            this.gl.bindBuffer(this.gl.ARRAY_BUFFER, buffer);
            this.gl.bufferData(this.gl.ARRAY_BUFFER, positions, this.gl.STATIC_DRAW);

            const posLoc = this.gl.getAttribLocation(this.program, 'position');
            this.gl.enableVertexAttribArray(posLoc);
            this.gl.vertexAttribPointer(posLoc, 2, this.gl.FLOAT, false, 0, 0);

            // Get Uniform Locations
            this.uniforms = {
                iTime: this.gl.getUniformLocation(this.program, 'iTime'),
                iResolution: this.gl.getUniformLocation(this.program, 'iResolution'),
                rayPos: this.gl.getUniformLocation(this.program, 'rayPos'),
                rayDir: this.gl.getUniformLocation(this.program, 'rayDir'),
                raysColor: this.gl.getUniformLocation(this.program, 'raysColor'),
                raysSpeed: this.gl.getUniformLocation(this.program, 'raysSpeed'),
                lightSpread: this.gl.getUniformLocation(this.program, 'lightSpread'),
                rayLength: this.gl.getUniformLocation(this.program, 'rayLength'),
                pulsating: this.gl.getUniformLocation(this.program, 'pulsating'),
                fadeDistance: this.gl.getUniformLocation(this.program, 'fadeDistance'),
                saturation: this.gl.getUniformLocation(this.program, 'saturation'),
                mousePos: this.gl.getUniformLocation(this.program, 'mousePos'),
                mouseInfluence: this.gl.getUniformLocation(this.program, 'mouseInfluence'),
                noiseAmount: this.gl.getUniformLocation(this.program, 'noiseAmount'),
                distortion: this.gl.getUniformLocation(this.program, 'distortion')
            };

            // Bind Event Listeners
            this._onResize = this.onResize.bind(this);
            window.addEventListener('resize', this._onResize);

            if (window.ResizeObserver) {
                this.resizeObserver = new ResizeObserver(() => this.onResize());
                this.resizeObserver.observe(this.container);
            }

            this.onResize();

            // Initial uniform values setup
            const rgb = this.hexToRgb(this.raysColor);
            this.gl.uniform3fv(this.uniforms.raysColor, new Float32Array(rgb));
            this.gl.uniform1f(this.uniforms.raysSpeed, this.raysSpeed);
            this.gl.uniform1f(this.uniforms.lightSpread, this.lightSpread);
            this.gl.uniform1f(this.uniforms.rayLength, this.rayLength);
            this.gl.uniform1f(this.uniforms.pulsating, this.pulsating ? 1.0 : 0.0);
            this.gl.uniform1f(this.uniforms.fadeDistance, this.fadeDistance);
            this.gl.uniform1f(this.uniforms.saturation, this.saturation);
            this.gl.uniform1f(this.uniforms.mouseInfluence, this.mouseInfluence);
            this.gl.uniform1f(this.uniforms.noiseAmount, this.noiseAmount);
            this.gl.uniform1f(this.uniforms.distortion, this.distortion);

            if (this.followMouse) {
                this._onMouseMove = this.onMouseMove.bind(this);
                window.addEventListener('mousemove', this._onMouseMove);
            }

            // Setup Intersection Observer to pause when off-screen
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    this.isPaused = !entry.isIntersecting;
                });
            }, { threshold: 0.1 });
            this.observer.observe(this.container);

            // Start loop
            this.loop(performance.now());
        }

        onMouseMove(e) {
            const rect = this.container.getBoundingClientRect();
            this.mouse.x = (e.clientX - rect.left) / rect.width;
            this.mouse.y = (e.clientY - rect.top) / rect.height;
        }

        onResize() {
            if (!this.container || !this.canvas || !this.gl) return;
            const rect = this.container.getBoundingClientRect();
            const wCSS = Math.max(1, Math.floor(rect.width));
            const hCSS = Math.max(1, Math.floor(rect.height));

            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            const w = wCSS * dpr;
            const h = hCSS * dpr;

            this.canvas.width = w;
            this.canvas.height = h;

            this.gl.viewport(0, 0, w, h);
            this.gl.uniform2f(this.uniforms.iResolution, w, h);

            const { anchor, dir } = this.getAnchorAndDir(this.raysOrigin, w, h);
            this.gl.uniform2fv(this.uniforms.rayPos, new Float32Array(anchor));
            this.gl.uniform2fv(this.uniforms.rayDir, new Float32Array(dir));
        }

        updateOptions(options = {}) {
            if (!this.gl) return;
            this.gl.useProgram(this.program);
            if (options.raysColor !== undefined) {
                this.raysColor = options.raysColor;
                this.gl.uniform3fv(this.uniforms.raysColor, new Float32Array(this.hexToRgb(this.raysColor)));
            }
            if (options.raysSpeed !== undefined) {
                this.raysSpeed = options.raysSpeed;
                this.gl.uniform1f(this.uniforms.raysSpeed, this.raysSpeed);
            }
            if (options.lightSpread !== undefined) {
                this.lightSpread = options.lightSpread;
                this.gl.uniform1f(this.uniforms.lightSpread, this.lightSpread);
            }
            if (options.rayLength !== undefined) {
                this.rayLength = options.rayLength;
                this.gl.uniform1f(this.uniforms.rayLength, this.rayLength);
            }
            if (options.pulsating !== undefined) {
                this.pulsating = options.pulsating;
                this.gl.uniform1f(this.uniforms.pulsating, this.pulsating ? 1.0 : 0.0);
            }
            if (options.fadeDistance !== undefined) {
                this.fadeDistance = options.fadeDistance;
                this.gl.uniform1f(this.uniforms.fadeDistance, this.fadeDistance);
            }
            if (options.saturation !== undefined) {
                this.saturation = options.saturation;
                this.gl.uniform1f(this.uniforms.saturation, this.saturation);
            }
            if (options.mouseInfluence !== undefined) {
                this.mouseInfluence = options.mouseInfluence;
                this.gl.uniform1f(this.uniforms.mouseInfluence, this.mouseInfluence);
            }
            if (options.noiseAmount !== undefined) {
                this.noiseAmount = options.noiseAmount;
                this.gl.uniform1f(this.uniforms.noiseAmount, this.noiseAmount);
            }
            if (options.distortion !== undefined) {
                this.distortion = options.distortion;
                this.gl.uniform1f(this.uniforms.distortion, this.distortion);
            }
            if (options.raysOrigin !== undefined) {
                this.raysOrigin = options.raysOrigin;
                this.onResize();
            }
        }

        loop(t) {
            this.animationId = requestAnimationFrame(this.loop.bind(this));

            if (this.isPaused) return;

            if (this.followMouse && this.mouseInfluence > 0.0) {
                const smoothing = 0.95;
                this.smoothMouse.x = this.smoothMouse.x * smoothing + this.mouse.x * (1 - smoothing);
                this.smoothMouse.y = this.smoothMouse.y * smoothing + this.mouse.y * (1 - smoothing);
                this.gl.uniform2f(this.uniforms.mousePos, this.smoothMouse.x, 1.0 - this.smoothMouse.y);
            }

            this.gl.uniform1f(this.uniforms.iTime, (t - this.t0) * 0.001);
            this.gl.drawArrays(this.gl.TRIANGLES, 0, 3);
        }

        destroy() {
            if (this.animationId) cancelAnimationFrame(this.animationId);
            window.removeEventListener('resize', this._onResize);
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
            }
            if (this.followMouse && this._onMouseMove) {
                window.removeEventListener('mousemove', this._onMouseMove);
            }
            if (this.observer) {
                this.observer.disconnect();
            }
            if (this.canvas && this.canvas.parentNode) {
                this.canvas.parentNode.removeChild(this.canvas);
            }
        }
    }

    // Export globally for page integration
    window.Plasma = Plasma;
    window.LightRays = LightRays;

    // Export globally to hook up on dynamic additions if needed
    window.initializeJellyButtons = function () {
        // Jelly buttons removed
    };

    // Auto-boot on load
    document.addEventListener('DOMContentLoaded', () => {
        // Jelly buttons auto-boot removed
    });

    /**
     * Scroll-triggered reveal animations (Intersection Observer)
     * Used on the About page "What Makes Us Unique" timeline section
     */
    window.initScrollReveal = function() {
        const revealElements = document.querySelectorAll('.reveal-on-scroll');
        if (!revealElements.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Stagger the reveal within each timeline row
                    const cards = entry.target.querySelectorAll('.unique-card');
                    entry.target.classList.add('revealed');

                    // If there are nested cards, add staggered reveal
                    cards.forEach((card, index) => {
                        card.style.transitionDelay = `${index * 0.1}s`;
                    });

                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px'
        });

        revealElements.forEach(el => observer.observe(el));
    }

    /**
     * Timeline node pulse — intensifies glow when the section is in viewport
     */
    window.initTimelinePulse = function() {
        const section = document.getElementById('unique-section');
        if (!section) return;

        const nodes = section.querySelectorAll('.rounded-full');
        if (!nodes.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                nodes.forEach(node => {
                    if (entry.isIntersecting) {
                        node.style.animationPlayState = 'running';
                    } else {
                        node.style.animationPlayState = 'paused';
                    }
                });
            });
        }, { threshold: 0.1 });

        observer.observe(section);
    }

    /**
     * Viewport-Triggered Count-Up Animation Utility
     * Smoothly animates integers and decimals over exactly 1000ms when scrolled into view.
     */
    window.initCountUpAnimation = function() {
        const elements = document.querySelectorAll('.count-up-number');
        if (!elements.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseFloat(el.getAttribute('data-target'));
                    const duration = 1000; // Duration exactly 1000ms as requested
                    const start = 0;
                    const startTime = performance.now();
                    const isDecimal = el.getAttribute('data-decimal') === 'true';
                    const prefix = el.getAttribute('data-prefix') || '';
                    const suffix = el.getAttribute('data-suffix') || '';

                    function update(now) {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        
                        // Ease out quad
                        const ease = progress * (2 - progress);
                        const current = start + (target - start) * ease;

                        if (isDecimal) {
                            el.textContent = prefix + current.toFixed(1) + suffix;
                        } else {
                            el.textContent = prefix + Math.floor(current) + suffix;
                        }

                        if (progress < 1) {
                            requestAnimationFrame(update);
                        } else {
                            el.textContent = prefix + target + suffix;
                        }
                    }

                    requestAnimationFrame(update);
                    observer.unobserve(el);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '0px 0px -20px 0px'
        });

        elements.forEach(el => observer.observe(el));
    }

    // Export for external use
    window.initScrollReveal = initScrollReveal;
    window.initTimelinePulse = initTimelinePulse;
    window.initCountUpAnimation = initCountUpAnimation;
})();
