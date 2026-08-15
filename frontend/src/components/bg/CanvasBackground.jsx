import { useEffect, useRef } from 'react';

export default function CanvasBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Particle nodes for glass refraction
    const particleCount = Math.min(Math.floor((width * height) / 16000), 85);
    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 1.8 + 0.8,
        alpha: Math.random() * 0.5 + 0.25,
        color: i % 3 === 0 ? 'rgba(0, 229, 255,' : i % 3 === 1 ? 'rgba(167, 139, 250,' : 'rgba(244, 114, 182,',
      });
    }

    const mouse = { x: width / 2, y: height / 2, targetX: width / 2, targetY: height / 2, active: false };

    const handleMouseMove = (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    let time = 0;

    const render = () => {
      time += 0.008;
      // Smooth mouse follow
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      ctx.clearRect(0, 0, width, height);

      // Deep space base
      const bgGrad = ctx.createLinearGradient(0, 0, width, height);
      bgGrad.addColorStop(0, '#060913');
      bgGrad.addColorStop(0.5, '#090d1c');
      bgGrad.addColorStop(1, '#04060c');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Glowing Ambient Aurora Nebulae (Dynamic floating light sources)
      // 1. Cyan Nebula (Top-Left / Center-Left)
      const n1X = width * 0.22 + Math.sin(time * 0.8) * 60;
      const n1Y = height * 0.25 + Math.cos(time * 0.7) * 45;
      const grad1 = ctx.createRadialGradient(n1X, n1Y, 20, n1X, n1Y, width * 0.45);
      grad1.addColorStop(0, 'rgba(0, 229, 255, 0.16)');
      grad1.addColorStop(0.4, 'rgba(0, 229, 255, 0.06)');
      grad1.addColorStop(1, 'transparent');
      ctx.fillStyle = grad1;
      ctx.fillRect(0, 0, width, height);

      // 2. Violet / Indigo Nebula (Bottom-Right)
      const n2X = width * 0.78 + Math.cos(time * 0.6) * 70;
      const n2Y = height * 0.7 + Math.sin(time * 0.5) * 50;
      const grad2 = ctx.createRadialGradient(n2X, n2Y, 30, n2X, n2Y, width * 0.5);
      grad2.addColorStop(0, 'rgba(124, 58, 237, 0.18)');
      grad2.addColorStop(0.45, 'rgba(167, 139, 250, 0.07)');
      grad2.addColorStop(1, 'transparent');
      ctx.fillStyle = grad2;
      ctx.fillRect(0, 0, width, height);

      // 3. Magenta / Rose Accent Nebula (Center-Top)
      const n3X = width * 0.55 + Math.sin(time * 0.4) * 80;
      const n3Y = height * 0.4 + Math.cos(time * 0.9) * 40;
      const grad3 = ctx.createRadialGradient(n3X, n3Y, 10, n3X, n3Y, width * 0.35);
      grad3.addColorStop(0, 'rgba(244, 114, 182, 0.10)');
      grad3.addColorStop(0.5, 'rgba(244, 114, 182, 0.03)');
      grad3.addColorStop(1, 'transparent');
      ctx.fillStyle = grad3;
      ctx.fillRect(0, 0, width, height);

      // 4. Emerald Accent Flare (Bottom-Left)
      const n4X = width * 0.15 + Math.cos(time * 0.7) * 50;
      const n4Y = height * 0.85 + Math.sin(time * 0.6) * 40;
      const grad4 = ctx.createRadialGradient(n4X, n4Y, 10, n4X, n4Y, width * 0.3);
      grad4.addColorStop(0, 'rgba(16, 185, 129, 0.10)');
      grad4.addColorStop(0.5, 'rgba(16, 185, 129, 0.02)');
      grad4.addColorStop(1, 'transparent');
      ctx.fillStyle = grad4;
      ctx.fillRect(0, 0, width, height);

      // Interactive Cursor Glow Aura
      if (mouse.active) {
        const cursorGlow = ctx.createRadialGradient(mouse.x, mouse.y, 5, mouse.x, mouse.y, 220);
        cursorGlow.addColorStop(0, 'rgba(0, 229, 255, 0.12)');
        cursorGlow.addColorStop(0.5, 'rgba(167, 139, 250, 0.05)');
        cursorGlow.addColorStop(1, 'transparent');
        ctx.fillStyle = cursorGlow;
        ctx.fillRect(0, 0, width, height);
      }

      // Update & render crystalline particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `${p.color}${p.alpha})`;
        ctx.fill();

        // Connect with nearby particles with translucent glass filaments
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.12 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }

        // Mouse connection filament
        if (mouse.active) {
          const mdx = p.x - mouse.x;
          const mdy = p.y - mouse.y;
          const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
          if (mdist < 150) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(mouse.x, mouse.y);
            ctx.strokeStyle = `rgba(0, 229, 255, ${0.25 * (1 - mdist / 150)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 1 }}
    />
  );
}
