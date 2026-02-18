# RideConnect Animations Guide

## Overview
This guide provides a comprehensive reference for all animations and effects available in the RideConnect web application.

## Animation Files
- `css/animations.css` - Main animations library (40+ effects)
- `css/style.css` - Enhanced with animation support
- `css/dashboard.css` - Dashboard-specific animations
- `js/main.js` - JavaScript animation controllers

## Quick Reference

### Entrance Animations
Add these classes to elements for entrance effects:

```html
<!-- Fade and slide -->
<div class="fade-in-up">Content</div>
<div class="slide-in-left">Content</div>
<div class="slide-in-right">Content</div>

<!-- Scale and rotate -->
<div class="scale-in">Content</div>
<div class="rotate-in">Content</div>
<div class="bounce-in">Content</div>
```

### Continuous Animations
For ongoing animations:

```html
<!-- Motion effects -->
<div class="float-animation">Floating element</div>
<div class="pulse-animation">Pulsing element</div>
<div class="morphing-shape blob">Organic shape</div>

<!-- Loading -->
<div class="spinner">Loading...</div>
```

### Hover Effects
Interactive hover animations:

```html
<!-- Transform effects -->
<div class="hover-lift">Lifts on hover</div>
<div class="hover-scale">Scales on hover</div>
<div class="hover-rotate">Rotates on hover</div>
<div class="hover-glow">Glows on hover</div>
```

### Text Effects
Special text styling:

```html
<!-- Gradient and glow -->
<h1 class="gradient-text">Colorful text</h1>
<h2 class="neon-text">Glowing text</h2>

<!-- Interactive -->
<a class="animated-underline">Link with underline</a>
```

### Button Effects
Enhanced button interactions:

```html
<button class="btn btn-primary hover-lift button-press">
    Click me
</button>
```

### Background Effects
Animated backgrounds:

```html
<!-- Gradient animation -->
<section class="animated-gradient">
    Content with animated gradient
</section>

<!-- Glass effect -->
<div class="glass-effect">
    Frosted glass appearance
</div>
```

### Scroll Animations
Trigger animations on scroll:

```html
<div class="fade-in-scroll">
    Animates when scrolled into view
</div>
```

### Stagger Delays
Sequential animations:

```html
<div class="fade-in-up stagger-1">First (0.1s delay)</div>
<div class="fade-in-up stagger-2">Second (0.2s delay)</div>
<div class="fade-in-up stagger-3">Third (0.3s delay)</div>
<div class="fade-in-up stagger-4">Fourth (0.4s delay)</div>
<div class="fade-in-up stagger-5">Fifth (0.5s delay)</div>
<div class="fade-in-up stagger-6">Sixth (0.6s delay)</div>
```

## JavaScript Features

### Scroll Animation Observer
Automatically added to all `.fade-in-scroll` elements:

```javascript
// Elements become visible when scrolled into view
setupScrollAnimations();
```

### Particle Effects
Add floating particles to hero section:

```javascript
addParticleEffects();
```

### Scroll to Top Button
Automatically appears when scrolling down:

```javascript
// Button appears after 300px scroll
// Smooth scroll to top on click
```

### Navbar Scroll Effect
Navbar changes style on scroll:

```javascript
// Adds 'scrolled' class after 50px
addNavbarScrollEffect();
```

### Progress Indicator
Shows loading progress for API calls:

```javascript
const progress = showProgressIndicator();
progress.update(50); // Update to 50%
progress.complete(); // Complete and hide
```

## Dashboard Animations

### Stat Cards
Animated statistics:

```html
<div class="stat-card">
    <div class="stat-value">1000+</div>
    <div class="stat-label">Rides</div>
</div>
```

### Toggle Switch
Smooth toggle animation:

```html
<label class="toggle-switch">
    <input type="checkbox">
    <span class="toggle-slider"></span>
</label>
```

### Rating Stars
Interactive star rating:

```html
<div class="star-rating">
    <i class="fas fa-star" data-rating="1"></i>
    <i class="fas fa-star" data-rating="2"></i>
    <i class="fas fa-star" data-rating="3"></i>
    <i class="fas fa-star" data-rating="4"></i>
    <i class="fas fa-star" data-rating="5"></i>
</div>
```

### Profile Avatar
Shimmer effect:

```html
<div class="profile-avatar">
    <i class="fas fa-user"></i>
</div>
```

## Performance Considerations

### Reduced Motion
Respects user preferences:

```css
@media (prefers-reduced-motion: reduce) {
    /* Animations are minimized */
}
```

### Mobile Optimization
- Particles hidden on mobile
- Simplified animations for better performance
- Touch-friendly interactions

## Browser Support
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (with -webkit- prefixes)
- Mobile browsers: Optimized animations

## Best Practices

1. **Don't Overuse**: Use animations purposefully
2. **Performance**: Test on mobile devices
3. **Accessibility**: Respect reduced motion preferences
4. **Timing**: Keep animations under 0.5s for interactions
5. **Consistency**: Use similar animations for similar actions

## Examples

### Landing Page Hero
```html
<section class="hero animated-gradient">
    <div class="hero-content slide-in-left">
        <h1 class="gradient-text">Your Ride, Your Way</h1>
        <p class="fade-in-up stagger-1">Description</p>
        <button class="btn btn-primary hover-lift button-press">
            Get Started
        </button>
    </div>
    <div class="hero-image slide-in-right">
        <div class="phone-mockup float-animation">
            <!-- Content -->
        </div>
    </div>
</section>
```

### Feature Cards
```html
<div class="feature-card hover-lift fade-in-scroll stagger-1">
    <div class="feature-icon pulse-animation">
        <i class="fas fa-clock"></i>
    </div>
    <h3>Real-time Matching</h3>
    <p>Description</p>
</div>
```

### Modal with Glass Effect
```html
<div class="modal">
    <div class="modal-content glass-effect scale-in">
        <h2>Modal Title</h2>
        <p>Content</p>
    </div>
</div>
```

## Demo Page
Visit `animations-demo.html` to see all animations in action!

## Customization

### Modify Animation Duration
```css
.custom-animation {
    animation-duration: 1s; /* Change from default */
}
```

### Modify Animation Delay
```css
.custom-delay {
    animation-delay: 0.5s;
}
```

### Create Custom Animations
```css
@keyframes myCustomAnimation {
    from { /* start state */ }
    to { /* end state */ }
}

.my-element {
    animation: myCustomAnimation 1s ease-out;
}
```

## Troubleshooting

### Animation Not Working
1. Check if CSS file is loaded
2. Verify class name spelling
3. Check browser console for errors
4. Ensure element is visible

### Performance Issues
1. Reduce number of animated elements
2. Use `will-change` CSS property
3. Disable particles on mobile
4. Use `transform` and `opacity` for best performance

## Support
For issues or questions, refer to the main documentation or check the demo page.
