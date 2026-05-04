/**
 * RideConnect — Modern Animation Engine
 * Using Web Animations API + Intersection Observer
 */

// ── Animation Configuration ──────────────────────────────────
const ANIMATION_CONFIG = {
  duration: 600,
  easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
  threshold: 0.15,
  rootMargin: '0px 0px -80px 0px'
};

// ── Intersection Observer for Scroll Animations ─────────────
class ScrollAnimationObserver {
  constructor() {
    this.observer = new IntersectionObserver(
      (entries) => this.handleIntersection(entries),
      {
        threshold: ANIMATION_CONFIG.threshold,
        rootMargin: ANIMATION_CONFIG.rootMargin
      }
    );
    this.animatedElements = new Set();
  }

  observe(elements) {
    elements.forEach(el => {
      if (!this.animatedElements.has(el)) {
        this.observer.observe(el);
      }
    });
  }

  handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
        entry.target.classList.add('visible');
        this.animatedElements.add(entry.target);
        
        // Trigger custom animation if data attribute exists
        const animationType = entry.target.dataset.animation;
        if (animationType) {
          this.triggerAnimation(entry.target, animationType);
        }
      }
    });
  }

  triggerAnimation(element, type) {
    const animations = {
      'fade-up': [
        { opacity: 0, transform: 'translateY(40px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ],
      'fade-left': [
        { opacity: 0, transform: 'translateX(-40px)' },
        { opacity: 1, transform: 'translateX(0)' }
      ],
      'fade-right': [
        { opacity: 0, transform: 'translateX(40px)' },
        { opacity: 1, transform: 'translateX(0)' }
      ],
      'scale': [
        { opacity: 0, transform: 'scale(0.8)' },
        { opacity: 1, transform: 'scale(1)' }
      ],
      'rotate': [
        { opacity: 0, transform: 'rotate(-10deg) scale(0.9)' },
        { opacity: 1, transform: 'rotate(0) scale(1)' }
      ]
    };

    const keyframes = animations[type] || animations['fade-up'];
    
    element.animate(keyframes, {
      duration: ANIMATION_CONFIG.duration,
      easing: ANIMATION_CONFIG.easing,
      fill: 'forwards'
    });
  }

  disconnect() {
    this.observer.disconnect();
    this.animatedElements.clear();
  }
}

// ── Particle System ──────────────────────────────────────────
class ParticleSystem {
  constructor(container, count = 25) {
    this.container = container;
    this.count = count;
    this.particles = [];
  }

  init() {
    for (let i = 0; i < this.count; i++) {
      const particle = this.createParticle();
      this.particles.push(particle);
      this.container.appendChild(particle);
    }
  }

  createParticle() {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random positioning
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    // Random animation delay and duration
    particle.style.animationDelay = Math.random() * 12 + 's';
    particle.style.animationDuration = (Math.random() * 8 + 10) + 's';
    
    // Random size
    const size = Math.random() * 4 + 4;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    // Random opacity
    particle.style.opacity = Math.random() * 0.4 + 0.2;
    
    return particle;
  }

  destroy() {
    this.particles.forEach(p => p.remove());
    this.particles = [];
  }
}

// ── Button Ripple Effect ─────────────────────────────────────
function createRipple(event) {
  const button = event.currentTarget;
  const ripple = document.createElement('span');
  
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;
  
  ripple.className = 'ripple';
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';
  
  button.appendChild(ripple);
  
  ripple.animate([
    { transform: 'scale(0)', opacity: 1 },
    { transform: 'scale(4)', opacity: 0 }
  ], {
    duration: 600,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }).onfinish = () => ripple.remove();
}

// ── Counter Animation ────────────────────────────────────────
function animateCounter(element, target, duration = 2000) {
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;
  
  const timer = setInterval(() => {
    current += increment;
    
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    
    element.textContent = Math.floor(current) + '+';
  }, 16);
}

// ── Parallax Effect ──────────────────────────────────────────
class ParallaxController {
  constructor() {
    this.elements = [];
    this.ticking = false;
  }

  add(element, speed = 0.5) {
    this.elements.push({ element, speed });
  }

  update() {
    const scrolled = window.pageYOffset;
    
    this.elements.forEach(({ element, speed }) => {
      if (element) {
        const offset = scrolled * speed;
        element.style.transform = `translateY(${offset}px)`;
      }
    });
    
    this.ticking = false;
  }

  onScroll() {
    if (!this.ticking) {
      window.requestAnimationFrame(() => this.update());
      this.ticking = true;
    }
  }

  init() {
    window.addEventListener('scroll', () => this.onScroll(), { passive: true });
  }
}

// ── Smooth Scroll ────────────────────────────────────────────
function smoothScrollTo(target, duration = 800) {
  const targetElement = typeof target === 'string' 
    ? document.querySelector(target) 
    : target;
    
  if (!targetElement) return;
  
  const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - 80;
  const startPosition = window.pageYOffset;
  const distance = targetPosition - startPosition;
  let startTime = null;
  
  function animation(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const progress = Math.min(timeElapsed / duration, 1);
    
    // Easing function (ease-out-expo)
    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    
    window.scrollTo(0, startPosition + distance * ease);
    
    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  }
  
  requestAnimationFrame(animation);
}

// ── Navbar Scroll Effect ─────────────────────────────────────
class NavbarController {
  constructor(navbar) {
    this.navbar = navbar;
    this.lastScroll = 0;
    this.ticking = false;
  }

  update() {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
      this.navbar.classList.add('scrolled');
    } else {
      this.navbar.classList.remove('scrolled');
    }
    
    this.lastScroll = currentScroll;
    this.ticking = false;
  }

  onScroll() {
    if (!this.ticking) {
      window.requestAnimationFrame(() => this.update());
      this.ticking = true;
    }
  }

  init() {
    window.addEventListener('scroll', () => this.onScroll(), { passive: true });
  }
}

// ── Scroll-to-Top Button ─────────────────────────────────────
class ScrollToTopButton {
  constructor() {
    this.button = this.createButton();
    this.ticking = false;
  }

  createButton() {
    const button = document.createElement('button');
    button.className = 'scroll-to-top';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.setAttribute('aria-label', 'Scroll to top');
    button.addEventListener('click', () => smoothScrollTo(document.body, 600));
    document.body.appendChild(button);
    return button;
  }

  update() {
    if (window.pageYOffset > 400) {
      this.button.classList.add('visible');
    } else {
      this.button.classList.remove('visible');
    }
    this.ticking = false;
  }

  onScroll() {
    if (!this.ticking) {
      window.requestAnimationFrame(() => this.update());
      this.ticking = true;
    }
  }

  init() {
    window.addEventListener('scroll', () => this.onScroll(), { passive: true });
  }
}

// ── Progress Indicator ───────────────────────────────────────
class ProgressIndicator {
  constructor() {
    this.indicator = this.createIndicator();
  }

  createIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'progress-indicator';
    document.body.appendChild(indicator);
    return indicator;
  }

  show() {
    this.indicator.style.display = 'block';
    this.indicator.style.width = '0%';
  }

  update(percent) {
    this.indicator.style.width = percent + '%';
  }

  complete() {
    this.indicator.style.width = '100%';
    setTimeout(() => {
      this.indicator.style.display = 'none';
    }, 300);
  }
}

// ── Modal Animations ─────────────────────────────────────────
function showModalWithAnimation(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  
  modal.style.display = 'block';
  
  // Animate backdrop
  modal.animate([
    { opacity: 0 },
    { opacity: 1 }
  ], {
    duration: 300,
    easing: 'ease-out',
    fill: 'forwards'
  });
  
  // Animate modal content
  const content = modal.querySelector('.modal-content');
  if (content) {
    content.animate([
      { opacity: 0, transform: 'translateY(-40px) scale(0.96)' },
      { opacity: 1, transform: 'translateY(0) scale(1)' }
    ], {
      duration: 400,
      easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
      fill: 'forwards'
    });
  }
}

function closeModalWithAnimation(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  
  const content = modal.querySelector('.modal-content');
  
  const animations = [];
  
  // Animate modal content
  if (content) {
    animations.push(
      content.animate([
        { opacity: 1, transform: 'translateY(0) scale(1)' },
        { opacity: 0, transform: 'translateY(-20px) scale(0.98)' }
      ], {
        duration: 250,
        easing: 'ease-in',
        fill: 'forwards'
      }).finished
    );
  }
  
  // Animate backdrop
  animations.push(
    modal.animate([
      { opacity: 1 },
      { opacity: 0 }
    ], {
      duration: 250,
      easing: 'ease-in',
      fill: 'forwards'
    }).finished
  );
  
  Promise.all(animations).then(() => {
    modal.style.display = 'none';
  });
}

// ── Initialize All Animations ────────────────────────────────
function initializeAnimations() {
  // Scroll animations
  const scrollObserver = new ScrollAnimationObserver();
  const animatedElements = document.querySelectorAll('.fade-in-scroll');
  scrollObserver.observe(animatedElements);
  
  // Particle system for hero
  const hero = document.querySelector('.hero');
  if (hero && window.innerWidth > 768) {
    const particles = new ParticleSystem(hero, 25);
    particles.init();
  }
  
  // Button ripples
  document.addEventListener('click', (e) => {
    const button = e.target.closest('.btn');
    if (button) {
      createRipple(e);
    }
  });
  
  // Parallax
  const parallax = new ParallaxController();
  const heroContent = document.querySelector('.hero-content');
  const heroImage = document.querySelector('.hero-image');
  if (heroContent) parallax.add(heroContent, 0.2);
  if (heroImage) parallax.add(heroImage, 0.4);
  parallax.init();
  
  // Navbar
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const navbarController = new NavbarController(navbar);
    navbarController.init();
  }
  
  // Scroll to top
  const scrollToTop = new ScrollToTopButton();
  scrollToTop.init();
  
  // Counter animations
  const counters = document.querySelectorAll('.stat h3');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.textContent) || 1000;
        animateCounter(entry.target, target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  
  counters.forEach(counter => counterObserver.observe(counter));
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        smoothScrollTo(target);
      }
    });
  });
  
  // Enhanced modal functions
  window.showModal = showModalWithAnimation;
  window.closeModal = closeModalWithAnimation;
  
  // Progress indicator for fetch requests
  const progressIndicator = new ProgressIndicator();
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    progressIndicator.show();
    progressIndicator.update(30);
    
    return originalFetch.apply(this, args)
      .then(response => {
        progressIndicator.update(70);
        return response;
      })
      .finally(() => {
        progressIndicator.complete();
      });
  };
}

// ── Auto-initialize on DOM ready ─────────────────────────────
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAnimations);
} else {
  initializeAnimations();
}

// Export for use in other modules
window.RideConnectAnimations = {
  smoothScrollTo,
  animateCounter,
  createRipple,
  showModal: showModalWithAnimation,
  closeModal: closeModalWithAnimation,
  ScrollAnimationObserver,
  ParticleSystem,
  ParallaxController
};
