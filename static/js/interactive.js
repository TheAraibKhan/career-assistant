/* ===================================
   CURSOR GLOW & INTERACTIVE EFFECTS
   =================================== */

class CursorGlow {
  constructor() {
    this.createCursor();
    this.initEventListeners();
  }

  createCursor() {
    const cursor = document.createElement("div");
    cursor.className = "cursor-glow active";
    cursor.id = "cursorGlow";
    document.body.appendChild(cursor);
    this.cursor = cursor;
  }

  initEventListeners() {
    document.addEventListener("mousemove", (e) => this.updateCursorPosition(e));
    document.addEventListener("mouseenter", () => {
      if (this.cursor) this.cursor.classList.add("active");
    });
    document.addEventListener("mouseleave", () => {
      if (this.cursor) this.cursor.classList.remove("active");
    });
  }

  updateCursorPosition(e) {
    if (!this.cursor) return;

    const x = e.clientX;
    const y = e.clientY;

    this.cursor.style.left = x - 15 + "px";
    this.cursor.style.top = y - 15 + "px";

    // Add hover effect on interactive elements
    const target = e.target;
    if (this.isInteractive(target)) {
      this.cursor.style.width = "40px";
      this.cursor.style.height = "40px";
      this.cursor.style.borderColor = "#ec4899";
      this.cursor.style.boxShadow = "0 0 30px #ec4899, inset 0 0 30px #ec4899";
    } else {
      this.cursor.style.width = "30px";
      this.cursor.style.height = "30px";
      this.cursor.style.borderColor = "#a855f7";
      this.cursor.style.boxShadow = "0 0 20px #a855f7, inset 0 0 20px #a855f7";
    }
  }

  isInteractive(element) {
    const interactiveSelectors = [
      "a",
      "button",
      "input",
      "textarea",
      "select",
      '[role="button"]',
    ];
    return interactiveSelectors.some(
      (selector) => element.matches(selector) || element.closest(selector),
    );
  }
}

// ===================================
// SCROLL PROGRESS BAR
// ===================================

class ScrollProgressBar {
  constructor() {
    this.createProgressBar();
    this.initScrollListener();
  }

  createProgressBar() {
    const bar = document.createElement("div");
    bar.className = "scroll-progress-bar";
    bar.style.width = "0%";
    document.body.appendChild(bar);
    this.bar = bar;
  }

  initScrollListener() {
    window.addEventListener("scroll", () => this.updateProgress());
  }

  updateProgress() {
    const windowHeight =
      document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / windowHeight) * 100;
    if (this.bar) {
      this.bar.style.width = progress + "%";
    }
  }
}

// ===================================
// SCROLL REVEAL ANIMATIONS
// ===================================

class ScrollReveal {
  constructor() {
    this.observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -100px 0px",
    };
    this.initObserver();
  }

  initObserver() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("scroll-reveal-visible");
          entry.target.style.animation = "scrollReveal 0.8s ease-out forwards";
          // Unobserve after animation to prevent re-triggering
          this.observer.unobserve(entry.target);
        }
      });
    }, this.observerOptions);

    // Observe all elements with scroll-reveal class
    document.querySelectorAll(".scroll-reveal").forEach((element) => {
      this.observer.observe(element);
    });
  }

  observeElement(element) {
    if (element && this.observer) {
      this.observer.observe(element);
    }
  }
}

// ===================================
// SMOOTH HOVER ANIMATIONS
// ===================================

class HoverAnimations {
  constructor() {
    this.initHoverEffects();
  }

  initHoverEffects() {
    // Glass cards
    document.addEventListener("mouseover", (e) => {
      const card = e.target.closest(".glass-card, .glass-card-premium");
      if (card) {
        card.style.transform = "translateY(-4px)";
        card.style.boxShadow = "0 0 40px rgba(168, 85, 247, 0.4)";
      }
    });

    document.addEventListener("mouseout", (e) => {
      const card = e.target.closest(".glass-card, .glass-card-premium");
      if (card) {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "";
      }
    });

    // Buttons
    document.addEventListener("mouseover", (e) => {
      const btn = e.target.closest(
        ".btn-primary, .btn-secondary, .btn-outline",
      );
      if (btn && !btn.matches("button[disabled]")) {
        btn.style.transform = "translateY(-2px)";
      }
    });

    document.addEventListener("mouseout", (e) => {
      const btn = e.target.closest(
        ".btn-primary, .btn-secondary, .btn-outline",
      );
      if (btn) {
        btn.style.transform = "translateY(0)";
      }
    });
  }
}

// ===================================
// INITIALIZE ALL EFFECTS
// ===================================

document.addEventListener("DOMContentLoaded", () => {
  new CursorGlow();
  new ScrollProgressBar();
  new ScrollReveal();
  new HoverAnimations();
});

// Fallback for already loaded DOM
if (document.readyState !== "loading") {
  new CursorGlow();
  new ScrollProgressBar();
  new ScrollReveal();
  new HoverAnimations();
}
