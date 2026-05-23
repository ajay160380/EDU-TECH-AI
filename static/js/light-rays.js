/**
 * LightRays WebGL Cinematic Background Component
 * Wraps OGL library to create smooth, high-performance mouse-responsive light ray effects.
 */
class LightRays {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        if (!this.container) return;

        this.options = Object.assign({
            raysOrigin: 'top-center',
            raysColor: '#ffffff',
            raysSpeed: 1.0,
            lightSpread: 1.0,
            rayLength: 2.0,
            pulsating: false,
            fadeDistance: 1.0,
            saturation: 1.0,
            followMouse: true,
            mouseInfluence: 0.1,
            noiseAmount: 0.02,
            distortion: 0.05
        }, options);

        this.mouse = { x: 0.5, y: 0.5 };
        this.smoothMouse = { x: 0.5, y: 0.5 };
        this.isVisible = false;
        this.animationId = null;
        this.cleanup = null;

        this.init();
    }

    // Hex to RGB converter
    hexToRgb(hex) {
        const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return m ? [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255] : [1, 1, 1];
    }

    // Calculate light ray origin anchor coordinates and ray direction vectors
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
        // Ensure relative container constraints for background floating canvas
        if (window.getComputedStyle(this.container).position === 'static') {
            this.container.style.position = 'relative';
        }

        // Setup performance-saving viewport observer
        this.observer = new IntersectionObserver((entries) => {
            const entry = entries[0];
            if (entry.isIntersecting) {
                if (!this.isVisible) {
                    this.isVisible = true;
                    this.startWebGL();
                }
            } else {
                if (this.isVisible) {
                    this.isVisible = false;
                    this.stopWebGL();
                }
            }
        }, { threshold: 0.1 });
        this.observer.observe(this.container);

        if (this.options.followMouse) {
            this.handleMouseMove = (e) => {
                const rect = this.container.getBoundingClientRect();
                this.mouse.x = (e.clientX - rect.left) / rect.width;
                this.mouse.y = (e.clientY - rect.top) / rect.height;
            };
            window.addEventListener('mousemove', this.handleMouseMove);
        }
    }

    startWebGL() {
        if (!window.OGL) {
            console.error('OGL library not loaded.');
            return;
        }

        // Setup Renderer
        const renderer = new window.OGL.Renderer({
            dpr: Math.min(window.devicePixelRatio, 2),
            alpha: true
        });
        this.renderer = renderer;
        const gl = renderer.gl;

        gl.canvas.style.position = 'absolute';
        gl.canvas.style.top = '0';
        gl.canvas.style.left = '0';
        gl.canvas.style.width = '100%';
        gl.canvas.style.height = '100%';
        gl.canvas.style.pointerEvents = 'none';
        gl.canvas.style.zIndex = '0';

        this.container.appendChild(gl.canvas);

        const vert = `
            attribute vec2 position;
            varying vec2 vUv;
            void main() {
                vUv = position * 0.5 + 0.5;
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;

        const frag = `
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
            varying vec2 vUv;

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
                combined = pow(combined, 0.7); // Boost mid-tones for visibility
                combined *= 1.5; // Overall intensity boost
                vec3 finalColor = raysColor * combined;
                
                if (noiseAmount > 0.0) {
                    float n = noise(coord * 0.01 + iTime * 0.05);
                    finalColor *= (1.0 - noiseAmount + noiseAmount * n);
                }

                if (saturation != 1.0) {
                    float gray = dot(finalColor, vec3(0.299, 0.587, 0.114));
                    finalColor = mix(vec3(gray), finalColor, saturation);
                }

                gl_FragColor = vec4(finalColor, combined);
            }
        `;

        const uniforms = {
            iTime: { value: 0 },
            iResolution: { value: [1, 1] },
            rayPos: { value: [0, 0] },
            rayDir: { value: [0, 1] },
            raysColor: { value: this.hexToRgb(this.options.raysColor) },
            raysSpeed: { value: this.options.raysSpeed },
            lightSpread: { value: this.options.lightSpread },
            rayLength: { value: this.options.rayLength },
            pulsating: { value: this.options.pulsating ? 1.0 : 0.0 },
            fadeDistance: { value: this.options.fadeDistance },
            saturation: { value: this.options.saturation },
            mousePos: { value: [0.5, 0.5] },
            mouseInfluence: { value: this.options.mouseInfluence },
            noiseAmount: { value: this.options.noiseAmount },
            distortion: { value: this.options.distortion }
        };
        this.uniforms = uniforms;

        const geometry = new window.OGL.Triangle(gl);
        const program = new window.OGL.Program(gl, {
            vertex: vert,
            fragment: frag,
            uniforms,
            transparent: true
        });
        const mesh = new window.OGL.Mesh(gl, { geometry, program });
        this.mesh = mesh;

        const updatePlacement = () => {
            if (!this.container || !renderer) return;
            const { clientWidth: wCSS, clientHeight: hCSS } = this.container;
            renderer.setSize(wCSS, hCSS);
            const dpr = renderer.dpr;
            const w = wCSS * dpr;
            const h = hCSS * dpr;
            
            uniforms.iResolution.value = [w, h];
            const { anchor, dir } = this.getAnchorAndDir(this.options.raysOrigin, w, h);
            uniforms.rayPos.value = anchor;
            uniforms.rayDir.value = dir;
        };

        const loop = (t) => {
            if (!this.renderer || !this.uniforms || !this.mesh) return;
            
            this.uniforms.iTime.value = t * 0.001;
            
            if (this.options.followMouse && this.options.mouseInfluence > 0.0) {
                const smoothing = 0.95;
                this.smoothMouse.x = this.smoothMouse.x * smoothing + this.mouse.x * (1 - smoothing);
                this.smoothMouse.y = this.smoothMouse.y * smoothing + this.mouse.y * (1 - smoothing);
                this.uniforms.mousePos.value = [this.smoothMouse.x, 1.0 - this.smoothMouse.y];
            }

            renderer.render({ scene: mesh });
            this.animationId = requestAnimationFrame(loop);
        };

        this.resizeHandler = updatePlacement;
        window.addEventListener('resize', this.resizeHandler);
        updatePlacement();
        this.animationId = requestAnimationFrame(loop);
    }

    stopWebGL() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
            this.resizeHandler = null;
        }
        if (this.renderer && this.renderer.gl.canvas.parentNode) {
            this.renderer.gl.canvas.parentNode.removeChild(this.renderer.gl.canvas);
        }
        this.renderer = null;
        this.mesh = null;
        this.uniforms = null;
    }

    destroy() {
        this.stopWebGL();
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        if (this.handleMouseMove) {
            window.removeEventListener('mousemove', this.handleMouseMove);
            this.handleMouseMove = null;
        }
    }
}
window.LightRays = LightRays;
