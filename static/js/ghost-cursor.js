/**
 * GhostCursor - A fluid, smoky cursor trail effect using Three.js shaders.
 * Natively converted to performant Vanilla JS for direct browser integration.
 */
class GhostCursor {
    constructor(options = {}) {
        this.color = options.color || '#2563eb';
        this.trailLength = options.trailLength || 20;
        this.inertia = options.inertia !== undefined ? options.inertia : 0.4;
        this.brightness = options.brightness !== undefined ? options.brightness : 1.4;
        this.grainIntensity = options.grainIntensity !== undefined ? options.grainIntensity : 0.04;
        this.fadeDelay = options.fadeDelayMs !== undefined ? options.fadeDelayMs : 200;
        this.fadeDuration = options.fadeDurationMs !== undefined ? options.fadeDurationMs : 1000;
        this.zIndex = options.zIndex !== undefined ? options.zIndex : 5;
        this.mixBlendMode = options.mixBlendMode || 'screen';

        this.container = null;
        this.renderer = null;
        this.scene = null;
        this.camera = null;
        this.geom = null;
        this.material = null;
        this.mesh = null;
        this.trailBuf = [];
        this.head = 0;
        this.raf = null;
        this.currentMouse = new THREE.Vector2(0.5, 0.5);
        this.velocity = new THREE.Vector2(0, 0);
        this.fadeOpacity = 0.0; // Start at 0, fade in on first movement
        this.lastMoveTime = performance.now();
        this.pointerActive = false;
        this.running = false;

        this.init();
    }

    init() {
        // Create full screen fixed container
        this.container = document.createElement('div');
        this.container.id = 'ghost-cursor-container';
        this.container.style.position = 'fixed';
        this.container.style.inset = '0';
        this.container.style.pointerEvents = 'none';
        this.container.style.zIndex = this.zIndex;
        document.body.appendChild(this.container);

        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        // Setup WebGL2 Renderer (highly performant and battery-friendly)
        this.renderer = new THREE.WebGLRenderer({
            antialias: !isTouch,
            alpha: true,
            depth: false,
            stencil: false,
            powerPreference: 'high-performance',
            premultipliedAlpha: false
        });
        
        this.renderer.setClearColor(0x000000, 0);
        this.renderer.domElement.style.pointerEvents = 'none';
        this.renderer.domElement.style.mixBlendMode = this.mixBlendMode;
        this.renderer.domElement.style.display = 'block';
        this.renderer.domElement.style.width = '100%';
        this.renderer.domElement.style.height = '100%';
        this.container.appendChild(this.renderer.domElement);

        this.scene = new THREE.Scene();
        this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        this.geom = new THREE.PlaneGeometry(2, 2);

        const maxTrail = Math.max(1, Math.floor(this.trailLength));
        this.trailBuf = Array.from({ length: maxTrail }, () => new THREE.Vector2(0.5, 0.5));
        this.head = 0;

        const baseColor = new THREE.Color(this.color);
        
        // Vertex Shader
        const vertexShader = `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = vec4(position, 1.0);
            }
        `;

        // Fragment Shader with Fluid FBM simulation, film grain, and additive bloom glow
        const fragmentShader = `
            #define MAX_TRAIL_LENGTH ${maxTrail}
            
            uniform float iTime;
            uniform vec3  iResolution;
            uniform vec2  iMouse;
            uniform vec2  iPrevMouse[MAX_TRAIL_LENGTH];
            uniform float iOpacity;
            uniform float iScale;
            uniform vec3  iBaseColor;
            uniform float iBrightness;
            uniform float iGrainIntensity;

            varying vec2  vUv;

            float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7))) * 43758.5453123); }
            float hash1(float n){ return fract(sin(n)*43758.5453); }

            float noise(vec2 p){
                vec2 i = floor(p), f = fract(p);
                f = f * f * (3. - 2. * f);
                return mix(mix(hash(i + vec2(0.,0.)), hash(i + vec2(1.,0.)), f.x),
                           mix(hash(i + vec2(0.,1.)), hash(i + vec2(1.,1.)), f.x), f.y);
            }

            float fbm(vec2 p){
                float v = 0.0;
                float a = 0.5;
                mat2 m = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
                for(int i=0;i<5;i++){
                    v += a * noise(p);
                    p = m * p * 2.0;
                    a *= 0.5;
                }
                return v;
            }

            vec3 tint1(vec3 base){ return mix(base, vec3(1.0), 0.15); }
            vec3 tint2(vec3 base){ return mix(base, vec3(0.8, 0.9, 1.0), 0.25); }

            vec4 blob(vec2 p, vec2 mousePos, float intensity, float activity) {
                vec2 q = vec2(fbm(p * iScale + iTime * 0.1), fbm(p * iScale + vec2(5.2,1.3) + iTime * 0.1));
                vec2 r = vec2(fbm(p * iScale + q * 1.5 + iTime * 0.15), fbm(p * iScale + q * 1.5 + vec2(8.3,2.8) + iTime * 0.15));
                float smoke = fbm(p * iScale + r * 0.8);
                
                float radius = 0.5 + 0.3 * (1.0 / iScale);
                float distFactor = 1.0 - smoothstep(0.0, radius * activity, length(p - mousePos));
                float alpha = pow(smoke, 2.5) * distFactor;

                vec3 c1 = tint1(iBaseColor);
                vec3 c2 = tint2(iBaseColor);
                vec3 color = mix(c1, c2, sin(iTime * 0.5) * 0.5 + 0.5);

                return vec4(color * alpha * intensity, alpha * intensity);
            }

            void main() {
                vec2 uv = (gl_FragCoord.xy / iResolution.xy * 2.0 - 1.0) * vec2(iResolution.x / iResolution.y, 1.0);
                vec2 mouse = (iMouse * 2.0 - 1.0) * vec2(iResolution.x / iResolution.y, 1.0);
                
                vec3 colorAcc = vec3(0.0);
                float alphaAcc = 0.0;
                
                vec4 b = blob(uv, mouse, 1.0, iOpacity);
                colorAcc += b.rgb;
                alphaAcc += b.a;

                for (int i = 0; i < MAX_TRAIL_LENGTH; i++) {
                    vec2 pm = (iPrevMouse[i] * 2.0 - 1.0) * vec2(iResolution.x / iResolution.y, 1.0);
                    float t = 1.0 - float(i) / float(MAX_TRAIL_LENGTH);
                    t = pow(t, 2.0);
                    
                    if (t > 0.01) {
                        vec4 bt = blob(uv, pm, t * 0.8, iOpacity);
                        colorAcc += bt.rgb;
                        alphaAcc += bt.a;
                    }
                }

                colorAcc *= iBrightness;
                float outAlpha = clamp(alphaAcc * iOpacity, 0.0, 1.0);
                
                // Add Film Grain overlay directly in shader for blazing speed!
                float grain = hash1(vUv.x*1000.0 + vUv.y*2000.0 + iTime) * 2.0 - 1.0;
                colorAcc += grain * iGrainIntensity * colorAcc;
                
                gl_FragColor = vec4(colorAcc, outAlpha);
            }
        `;

        this.material = new THREE.ShaderMaterial({
            uniforms: {
                iTime: { value: 0 },
                iResolution: { value: new THREE.Vector3(1, 1, 1) },
                iMouse: { value: new THREE.Vector2(0.5, 0.5) },
                iPrevMouse: { value: this.trailBuf.map(v => v.clone()) },
                iOpacity: { value: 0.0 },
                iScale: { value: 1.0 },
                iBaseColor: { value: new THREE.Vector3(baseColor.r, baseColor.g, baseColor.b) },
                iBrightness: { value: this.brightness },
                iGrainIntensity: { value: this.grainIntensity }
            },
            vertexShader,
            fragmentShader,
            transparent: true,
            depthTest: false,
            depthWrite: false
        });

        this.mesh = new THREE.Mesh(this.geom, this.material);
        this.scene.add(this.mesh);

        this.resize();
        this._resizeHandler = () => this.resize();
        window.addEventListener('resize', this._resizeHandler);

        // Event Listeners for tracking cursor
        const onPointerMove = (e) => {
            const x = THREE.MathUtils.clamp(e.clientX / window.innerWidth, 0, 1);
            const y = THREE.MathUtils.clamp(1 - e.clientY / window.innerHeight, 0, 1);
            
            this.currentMouse.set(x, y);
            this.pointerActive = true;
            this.lastMoveTime = performance.now();
            this.ensureLoop();
        };

        const onPointerLeave = () => {
            this.pointerActive = false;
            this.lastMoveTime = performance.now();
            this.ensureLoop();
        };

        window.addEventListener('pointermove', onPointerMove, { passive: true });
        window.addEventListener('pointerleave', onPointerLeave, { passive: true });
        
        // Clean up listeners on destroy
        this._destroyListeners = () => {
            window.removeEventListener('pointermove', onPointerMove);
            window.removeEventListener('pointerleave', onPointerLeave);
            window.removeEventListener('resize', this._resizeHandler);
        };

        this.t0 = performance.now();
        this.ensureLoop();
    }

    resize() {
        const cssW = window.innerWidth;
        const cssH = window.innerHeight;
        const currentDPR = Math.min(window.devicePixelRatio || 1, 2);
        
        this.renderer.setPixelRatio(currentDPR);
        this.renderer.setSize(cssW, cssH);

        const wpx = cssW * currentDPR;
        const hpx = cssH * currentDPR;
        
        this.material.uniforms.iResolution.value.set(wpx, hpx, 1);
        this.material.uniforms.iScale.value = Math.max(0.5, Math.min(2.0, Math.min(cssW, cssH) / 600));
    }

    updateColor(colorHex) {
        this.color = colorHex;
        if (this.material) {
            const c = new THREE.Color(colorHex);
            this.material.uniforms.iBaseColor.value.set(c.r, c.g, c.b);
        }
    }

    ensureLoop() {
        if (!this.running) {
            this.running = true;
            this.raf = requestAnimationFrame(() => this.animate());
        }
    }

    animate() {
        if (!this.running) return;

        const now = performance.now();
        const t = (now - this.t0) / 1000;

        if (this.pointerActive) {
            this.velocity.set(
                this.currentMouse.x - this.material.uniforms.iMouse.value.x,
                this.currentMouse.y - this.material.uniforms.iMouse.value.y
            );
            this.material.uniforms.iMouse.value.copy(this.currentMouse);
            // Ease opacity in on first movement
            this.fadeOpacity = Math.min(1.0, this.fadeOpacity + 0.1);
        } else {
            this.velocity.multiplyScalar(this.inertia);
            if (this.velocity.lengthSq() > 1e-6) {
                this.material.uniforms.iMouse.value.add(this.velocity);
            }
            
            const dt = now - this.lastMoveTime;
            if (dt > this.fadeDelay) {
                const k = Math.min(1, (dt - this.fadeDelay) / this.fadeDuration);
                this.fadeOpacity = Math.max(0, 1 - k);
            }
        }

        const N = this.trailBuf.length;
        this.head = (this.head + 1) % N;
        this.trailBuf[this.head].copy(this.material.uniforms.iMouse.value);
        
        const arr = this.material.uniforms.iPrevMouse.value;
        for (let i = 0; i < N; i++) {
            const srcIdx = (this.head - i + N) % N;
            arr[i].copy(this.trailBuf[srcIdx]);
        }

        this.material.uniforms.iOpacity.value = this.fadeOpacity;
        this.material.uniforms.iTime.value = t;

        this.renderer.render(this.scene, this.camera);

        if (!this.pointerActive && this.fadeOpacity <= 0.001) {
            this.running = false;
            this.raf = null;
            return;
        }

        this.raf = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        this.running = false;
        if (this.raf) cancelAnimationFrame(this.raf);
        if (this._destroyListeners) this._destroyListeners();
        
        this.scene.clear();
        this.geom.dispose();
        this.material.dispose();
        this.renderer.dispose();
        
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Bind to window to prevent global scoping conflicts
window.GhostCursor = GhostCursor;
