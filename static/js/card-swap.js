/**
 * CardSwap Animation Class
 * Premium 3D Swing & Perspective Stack Engine
 * Dynamic Depth-of-Field Blur & Opacity Scale (Subtle &legible)
 * Robust GSAP-to-CSS 3D Hardware Accelerated Fallback Engine
 * Ported from React to Vanilla JS + GSAP for Django Template Integration
 */

class CardSwap {
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) return;

        this.cards = Array.from(this.container.querySelectorAll('.card-swap-item'));
        if (this.cards.length === 0) return;

        // Configuration (Increased distances for beautiful premium depth)
        this.cardDistance = options.cardDistance || 32;
        this.verticalDistance = options.verticalDistance || 30;
        this.delay = options.delay || 2000;
        
        // 3D Isometric Angles (Set to 0 for perfectly straight, aligned cards)
        this.rotX = 0;
        this.rotY = 0;

        // Animation Timings (Buttery smooth, snappy and highly satisfying)
        this.config = {
            easeDrop: 'power3.inOut',
            easeMove: 'power3.out',
            easeReturn: 'power3.out',
            durDrop: 0.75,
            durMove: 0.75,
            durReturn: 0.75,
            promoteOverlap: 0.88,
            returnDelay: 0.05
        };

        // State
        this.order = Array.from({ length: this.cards.length }, (_, i) => i);
        this.tl = null;
        this.interval = null;

        this.init();
    }

    makeSlot(i, total) {
        return {
            x: i * this.cardDistance,
            y: -i * this.verticalDistance,
            z: -i * this.cardDistance * 2.2, // Deeper perspective depth
            zIndex: total - i
        };
    }

    placeNow(el, slot, slotIndex = 0) {
        const slotOpacity = slotIndex === 0 ? 1 : (slotIndex === 1 ? 0.92 : (slotIndex === 2 ? 0.84 : 0.76));
        const slotBlur = slotIndex === 0 ? 0 : (slotIndex === 1 ? 0.5 : (slotIndex === 2 ? 1 : 1.5));

        if (typeof gsap !== 'undefined') {
            gsap.set(el, {
                x: slot.x,
                y: slot.y,
                z: slot.z,
                xPercent: -50,
                yPercent: -50,
                rotateX: this.rotX,
                rotateY: this.rotY,
                skewY: 0,
                opacity: slotOpacity,
                filter: `blur(${slotBlur}px)`,
                transformOrigin: 'center center',
                zIndex: slot.zIndex,
                force3D: true
            });
        } else {
            // Hardware Accelerated CSS Fallback Placement
            el.style.position = 'absolute';
            el.style.top = '50%';
            el.style.left = '50%';
            el.style.transform = `translate(-50%, -50%) translate3d(${slot.x}px, ${slot.y}px, ${slot.z}px) rotateX(${this.rotX}deg) rotateY(${this.rotY}deg) scale(1)`;
            el.style.zIndex = slot.zIndex;
            el.style.opacity = slotOpacity;
            el.style.filter = `blur(${slotBlur}px)`;
            el.style.transition = 'transform 0.75s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.75s ease, filter 0.75s ease, z-index 0.75s step-end';
        }
    }

    updateFrontClass() {
        const frontIndex = this.order[0];
        this.cards.forEach((card, i) => {
            if (i === frontIndex) {
                card.classList.add('is-front');
            } else {
                card.classList.remove('is-front');
            }
        });
    }

    swap() {
        if (this.order.length < 2) return;
        
        const frontIndex = this.order[0];
        const restIndices = this.order.slice(1);
        const elFront = this.cards[frontIndex];
        
        if (!elFront) return;

        // 1. Update internal order instantly to prevent race conditions or desync on manual interruption!
        this.order = [...restIndices, frontIndex];

        // 2. Manage front element highlighted state class
        this.updateFrontClass();

        // 3. Instant sidebar visual feedback at the start of the card transition!
        if (typeof window.onCardActive === 'function') {
            window.onCardActive(this.order[0]);
        }

        if (typeof gsap !== 'undefined') {
            this.tl = gsap.timeline();
            
            // Drop the front card down with an elegant 3D swing & fade out
            this.tl.to(elFront, {
                y: '+=380',
                rotateX: 18,
                rotateY: -35,
                scale: 0.8,
                opacity: 0,
                filter: 'blur(2px)',
                duration: this.config.durDrop,
                ease: this.config.easeDrop
            });

            // Promote all other cards forward in 3D space with dynamic DoF blur / opacity transitions
            this.tl.addLabel('promote', `-=${this.config.durDrop * this.config.promoteOverlap}`);
            
            restIndices.forEach((idx, i) => {
                const el = this.cards[idx];
                if (!el) return;
                
                const slot = this.makeSlot(i, this.cards.length);
                const slotOpacity = i === 0 ? 1 : (i === 1 ? 0.92 : (i === 2 ? 0.84 : 0.76));
                const slotBlur = i === 0 ? 0 : (i === 1 ? 0.5 : (i === 2 ? 1 : 1.5));

                this.tl.set(el, { zIndex: slot.zIndex }, 'promote');
                this.tl.to(
                    el,
                    {
                        x: slot.x,
                        y: slot.y,
                        z: slot.z,
                        rotateX: this.rotX,
                        rotateY: this.rotY,
                        opacity: slotOpacity,
                        filter: `blur(${slotBlur}px)`,
                        duration: this.config.durMove,
                        ease: this.config.easeMove
                    },
                    `promote+=${i * 0.08}`
                );
            });

            // Return the dropped card to the very back of the stack
            const backSlot = this.makeSlot(this.cards.length - 1, this.cards.length);
            const backOpacity = 0.76;
            const backBlur = 1.5;

            this.tl.addLabel('return', `promote+=${this.config.durMove * this.config.returnDelay}`);
            
            this.tl.call(() => {
                gsap.set(elFront, { zIndex: backSlot.zIndex });
            }, null, 'return');

            this.tl.to(
                elFront,
                {
                    x: backSlot.x,
                    y: backSlot.y,
                    z: backSlot.z,
                    rotateX: this.rotX,
                    rotateY: this.rotY,
                    scale: 1,
                    opacity: backOpacity,
                    filter: `blur(${backBlur}px)`,
                    duration: this.config.durReturn,
                    ease: this.config.easeReturn
                },
                'return'
            );
        } else {
            // Pure 3D Hardware Accelerated CSS Fallback Animation!
            // 1. Swing front card out and down elegantly
            elFront.style.transform = `translate(-50%, -50%) translate3d(${this.makeSlot(0, this.cards.length).x}px, 380px, 100px) rotateX(18deg) rotateY(-35deg) scale(0.8)`;
            elFront.style.opacity = 0;
            elFront.style.filter = 'blur(2px)';
            
            // 2. Slide remaining cards forward smoothly with DoF Blur & Opacity scale
            restIndices.forEach((idx, i) => {
                const el = this.cards[idx];
                if (!el) return;
                const slot = this.makeSlot(i, this.cards.length);
                const slotOpacity = i === 0 ? 1 : (i === 1 ? 0.92 : (i === 2 ? 0.84 : 0.76));
                const slotBlur = i === 0 ? 0 : (i === 1 ? 0.5 : (i === 2 ? 1 : 1.5));

                el.style.zIndex = slot.zIndex;
                el.style.transform = `translate(-50%, -50%) translate3d(${slot.x}px, ${slot.y}px, ${slot.z}px) rotateX(${this.rotX}deg) rotateY(${this.rotY}deg) scale(1)`;
                el.style.opacity = slotOpacity;
                el.style.filter = `blur(${slotBlur}px)`;
            });

            // 3. Return front card to the back cleanly at the end of the swing duration
            setTimeout(() => {
                const backSlot = this.makeSlot(this.cards.length - 1, this.cards.length);
                const backOpacity = 0.76;
                const backBlur = 1.5;

                elFront.style.zIndex = backSlot.zIndex;
                elFront.style.transform = `translate(-50%, -50%) translate3d(${backSlot.x}px, ${backSlot.y}px, ${backSlot.z}px) rotateX(${this.rotX}deg) rotateY(${this.rotY}deg) scale(1)`;
                elFront.style.opacity = backOpacity;
                elFront.style.filter = `blur(${backBlur}px)`;
            }, 380);
        }
    }

    start() {
        if (this.interval) clearInterval(this.interval);
        this.interval = setInterval(() => this.swap(), this.delay);
    }

    pause() {
        if (this.tl) this.tl.pause();
        if (this.interval) clearInterval(this.interval);
    }

    resume() {
        if (this.tl) this.tl.play();
        this.start();
    }

    jumpTo(index) {
        index = parseInt(index, 10);
        if (isNaN(index)) return;
        if (this.order[0] === index) return;
        
        const targetPos = this.order.indexOf(index);
        if (targetPos === -1) return;
        
        // 1. Clear auto-play timer and kill any active timeline animations in progress
        this.pause();
        if (this.tl) {
            this.tl.kill();
            this.tl = null;
        }
        
        // 2. Re-arrange order so target index is first
        const newOrder = [...this.order.slice(targetPos), ...this.order.slice(0, targetPos)];
        this.order = newOrder;

        // 3. Highlight front card state
        this.updateFrontClass();
        
        // 4. Animate all cards to their new slot layout beautifully
        this.cards.forEach((card, i) => {
            const slotIndex = this.order.indexOf(i);
            const slot = this.makeSlot(slotIndex, this.cards.length);
            const slotOpacity = slotIndex === 0 ? 1 : (slotIndex === 1 ? 0.92 : (slotIndex === 2 ? 0.84 : 0.76));
            const slotBlur = slotIndex === 0 ? 0 : (slotIndex === 1 ? 0.5 : (slotIndex === 2 ? 1 : 1.5));

            if (typeof gsap !== 'undefined') {
                // Set zIndex immediately to prevent clipping during movement
                gsap.set(card, { zIndex: slot.zIndex });
                
                gsap.to(card, {
                    x: slot.x,
                    y: slot.y,
                    z: slot.z,
                    rotateX: this.rotX,
                    rotateY: this.rotY,
                    scale: 1,
                    opacity: slotOpacity,
                    filter: `blur(${slotBlur}px)`,
                    duration: 0.7,
                    ease: 'power3.out'
                });
            } else {
                card.style.zIndex = slot.zIndex;
                card.style.opacity = slotOpacity;
                card.style.filter = `blur(${slotBlur}px)`;
                card.style.transform = `translate(-50%, -50%) translate3d(${slot.x}px, ${slot.y}px, ${slot.z}px) rotateX(${this.rotX}deg) rotateY(${this.rotY}deg) scale(1)`;
            }
        });
        
        // 5. Update the sidebar indicators
        if (typeof window.onCardActive === 'function') {
            window.onCardActive(index);
        }
        
        // 6. Start fresh autoplay timer
        this.start();
    }

    init() {
        // Initial Placement
        this.cards.forEach((card, i) => {
            this.placeNow(card, this.makeSlot(i, this.cards.length), i);
        });

        // Highlights front card state class
        this.updateFrontClass();

        // Start Animation Loop
        this.start();

        // Trigger initial active state
        if (typeof window.onCardActive === 'function') {
            window.onCardActive(this.order[0]);
        }
    }
}

// Robust Bulletproof Fail-safe Initialization Handler
// Ensures CardSwap initializes instantly when DOM is ready (with or without GSAP CDN)
function tryInitCardSwap() {
    if (!window.cardSwapInstance) {
        window.cardSwapInstance = new CardSwap('#card-swap-container', {
            delay: 2000,
            cardDistance: 25,
            verticalDistance: 25
        });
        console.log('[CardSwap] Initialized (GSAP loaded: ' + (typeof gsap !== 'undefined') + ')');
    }
    return true;
}

// Auto-initialize as soon as DOM is ready or wait up to 200ms for async GSAP scripts
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(tryInitCardSwap, 200);
});
