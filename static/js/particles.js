/* ===================================
   PARTICLE BACKGROUND ANIMATION
   =================================== */

class ParticleBackground {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext("2d");
    this.particles = [];
    this.particleCount = Math.min(50, Math.max(20, window.innerWidth / 30));

    this.resizeCanvas();
    this.initParticles();
    this.animate();

    window.addEventListener("resize", () => this.resizeCanvas());
  }

  resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  initParticles() {
    this.particles = [];
    const colors = ["#a855f7", "#ec4899", "#fbbf24"];

    for (let i = 0; i < this.particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 0.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        opacity: Math.random() * 0.5 + 0.2,
        life: Math.random() * 200 + 100,
        maxLife: Math.random() * 200 + 100,
      });
    }
  }

  animate = () => {
    // Clear canvas
    this.ctx.fillStyle = "#050505";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Update and draw particles
    this.particles.forEach((particle, index) => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.life--;

      // Wrap around screen
      if (particle.x < -10) particle.x = this.canvas.width + 10;
      if (particle.x > this.canvas.width + 10) particle.x = -10;
      if (particle.y < -10) particle.y = this.canvas.height + 10;
      if (particle.y > this.canvas.height + 10) particle.y = -10;

      // Fade out
      const fadeOpacity = particle.opacity * (particle.life / particle.maxLife);

      // Draw particle
      this.ctx.fillStyle = particle.color;
      this.ctx.globalAlpha = fadeOpacity;
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      this.ctx.fill();

      // Respawn if dead
      if (particle.life <= 0) {
        const colors = ["#a855f7", "#ec4899", "#fbbf24"];
        particle.x = Math.random() * this.canvas.width;
        particle.y = Math.random() * this.canvas.height;
        particle.color = colors[Math.floor(Math.random() * colors.length)];
        particle.life = particle.maxLife;
        particle.opacity = Math.random() * 0.5 + 0.2;
      }
    });

    // Draw connections
    this.ctx.strokeStyle = "rgba(168, 85, 247, 0.1)";
    this.ctx.lineWidth = 1;
    this.ctx.globalAlpha = 0.3;

    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 100) {
          this.ctx.globalAlpha = (1 - distance / 100) * 0.1;
          this.ctx.beginPath();
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.stroke();
        }
      }
    }

    this.ctx.globalAlpha = 1;
    requestAnimationFrame(this.animate);
  };
}

// Initialize on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new ParticleBackground("particleCanvas");
  });
} else {
  new ParticleBackground("particleCanvas");
}
