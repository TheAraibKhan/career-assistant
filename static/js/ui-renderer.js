/**
 * CareerAssist UI Renderer
 * Keeps all UI synchronized with state changes
 * Uses event-driven architecture for real-time updates
 */

class UIRenderer {
  constructor(appState) {
    this.appState = appState;
    this.cache = {}; // DOM element cache

    // Subscribe to all state changes
    this.appState.subscribe((prevState, newState) => {
      this._onStateChange(prevState, newState);
    });

    console.log("✓ UI Renderer initialized");
  }

  /**
   * Handle state changes and re-render affected UI
   */
  _onStateChange(prevState, newState) {
    // Detect what changed and update only those sections
    if (prevState.stats !== newState.stats) {
      this.updateStatCards(newState.stats);
      this.updateProgressRing(newState.stats);
    }

    if (prevState.skills !== newState.skills) {
      this.updateSkillTree(newState.skills);
    }

    if (prevState.roadmap !== newState.roadmap) {
      this.updateRoadmap(newState.roadmap.items);
    }

    console.log("UI re-rendered due to state change");
  }

  // ===== STAT CARDS =====

  /**
   * Update stat cards with real data
   */
  updateStatCards(stats) {
    const statCards = document.querySelectorAll(".stat-card");

    if (statCards[0]) {
      statCards[0].querySelector(".stat-value").textContent =
        stats.career_readiness + "%";
      const changeEl = statCards[0].querySelector(".stat-change");
      if (changeEl)
        changeEl.textContent = "↑ " + (stats.career_readiness || 0) + "%";
    }

    if (statCards[1]) {
      statCards[1].querySelector(".stat-value").textContent =
        stats.total_xp || 0;
      const changeEl = statCards[1].querySelector(".stat-change");
      if (changeEl)
        changeEl.textContent =
          stats.total_xp > 0 ? "↑ +" + stats.total_xp : "Start";
    }

    if (statCards[2]) {
      const skillCount = Object.keys(this.appState.state.skills).length;
      statCards[2].querySelector(".stat-value").textContent = skillCount || 0;
    }

    if (statCards[3]) {
      const tasksCompleted = stats.tasks_completed || 0;
      statCards[3].querySelector(".stat-value").textContent =
        tasksCompleted + "/5";
      const changeEl = statCards[3].querySelector(".stat-change");
      if (changeEl) changeEl.textContent = 5 - tasksCompleted + " left";
    }

    this._animateCardUpdate(statCards);
  }

  /**
   * Animate stat card updates
   */
  _animateCardUpdate(cards) {
    cards.forEach((card) => {
      card.style.opacity = "0.5";
      card.style.transform = "scale(0.95)";
      setTimeout(() => {
        card.style.transition = "all 0.3s ease-out";
        card.style.opacity = "1";
        card.style.transform = "scale(1)";
      }, 50);
    });
  }

  // ===== PROGRESS RING =====

  /**
   * Update the SVG progress ring
   */
  updateProgressRing(stats) {
    const ringValue = document.querySelector(".ring-value");
    if (ringValue) {
      ringValue.textContent = stats.career_readiness + "%";
    }

    const ringFill = document.getElementById("mainRingFill");
    if (ringFill) {
      const circumference = 314; // π * 2 * r = π * 100
      const offset = circumference * (1 - stats.career_readiness / 100);
      ringFill.style.transition = "stroke-dashoffset 0.6s ease-out";
      ringFill.style.strokeDashoffset = offset;
    }
  }

  // ===== SKILL TREE =====

  /**
   * Update skill tree with real data
   */
  updateSkillTree(skillsObj) {
    const skillTree = document.querySelector(".skill-tree");
    if (!skillTree) return;

    skillTree.innerHTML = "";

    Object.entries(skillsObj).forEach(([skillName, data]) => {
      const proficiency =
        data.level >= 3
          ? "Advanced"
          : data.level >= 2
            ? "Intermediate"
            : "Beginner";
      const progress = Math.min(100, (data.totalXp % 500) / 5);
      const color =
        data.level >= 3
          ? "fill-purple"
          : data.level >= 2
            ? "fill-pink"
            : "fill-green";

      const skillNode = document.createElement("div");
      skillNode.className = "skill-node";
      skillNode.innerHTML = `
        <div class="skill-icon-box" style="background: rgba(139, 92, 246, 0.15); color: #8b5cf6;">
          ${skillName.substring(0, 2).toUpperCase()}
        </div>
        <span class="skill-name">${skillName}</span>
        <div class="progress-bar-track" style="width: 80px;">
          <div class="progress-bar-fill ${color}" style="width: ${progress}%"></div>
        </div>
        <span class="skill-level level-${proficiency.toLowerCase()}">${proficiency}</span>
      `;
      skillTree.appendChild(skillNode);
    });
  }

  // ===== ROADMAP =====

  /**
   * Update roadmap with real milestones
   */
  updateRoadmap(roadmapItems) {
    const timeline = document.querySelector(".roadmap-timeline");
    if (!timeline) return;

    timeline.innerHTML = "";

    roadmapItems.forEach((item, idx) => {
      const dotClass =
        item.status === "completed"
          ? "completed"
          : item.status === "active"
            ? "active"
            : "locked";
      const dotIcon =
        item.status === "completed"
          ? "✓"
          : item.status === "active"
            ? "▶"
            : "—";
      const badgeClass =
        item.status === "completed"
          ? "badge-done"
          : item.status === "active"
            ? "badge-progress"
            : "badge-locked";
      const badge =
        item.status === "completed"
          ? `Completed · +${item.xp} XP`
          : item.status === "active"
            ? `In Progress · ${item.progress}%`
            : `Locked · Level ${5 + idx}`;

      const timelineItem = document.createElement("div");
      timelineItem.className = "timeline-item";
      timelineItem.innerHTML = `
        <div class="timeline-dot ${dotClass}">
          <div class="dot-icon">${dotIcon}</div>
        </div>
        <div class="timeline-content">
          <h4>${item.title}</h4>
          <p>${item.description || "Master this skill"}</p>
          <span class="timeline-badge ${badgeClass}">${badge}</span>
        </div>
      `;
      timeline.appendChild(timelineItem);
    });
  }

  // ===== STREAK =====

  /**
   * Update streak display
   */
  updateStreak(streak) {
    const streakFire = document.querySelector(".streak-fire");
    if (streakFire) {
      streakFire.textContent = streak;
    }

    const streakCount = document.querySelector(".streak-count");
    if (streakCount) {
      streakCount.textContent = `${streak}-Day Streak`;
    }
  }

  // ===== TASKS =====

  /**
   * Update task list with real tasks
   */
  updateTasks(tasks) {
    const taskList = document.querySelector(".task-list");
    if (!taskList) return;

    taskList.innerHTML = "";

    if (!tasks || tasks.length === 0) {
      taskList.innerHTML =
        '<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No tasks yet. Complete onboarding!</div>';
      return;
    }

    tasks.forEach((task, idx) => {
      const taskEl = document.createElement("div");
      taskEl.className = "task-item";
      taskEl.innerHTML = `
        <div class="task-check"></div>
        <div class="task-info">
          <div class="task-title">${task.title}</div>
          <div class="task-meta">${task.category || "Learning"} · Est. ${task.duration || "30 min"}</div>
        </div>
        <div class="task-xp">+${task.xp || 30} XP</div>
      `;

      taskEl.onclick = () => this._handleTaskClick(taskEl, task);
      taskList.appendChild(taskEl);
    });
  }

  /**
   * Handle task completion click
   */
  _handleTaskClick(taskEl, task) {
    if (taskEl.classList.contains("done")) {
      taskEl.classList.remove("done");
    } else {
      // Complete task via API
      this._completeTaskViaAPI(task);
    }
  }

  /**
   * Send task completion to API
   */
  async _completeTaskViaAPI(task) {
    try {
      const response = await fetch("/api/task-complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: task.title,
          xp: task.xp || 30,
          skill: task.skill || null,
        }),
      });

      const result = await response.json();

      if (result.success) {
        // Update app state with returned stats
        const { stats } = result;
        this.appState.setState({ stats });
        this._showXpToast(`+${task.xp || 30} XP Earned! ⚡`);
      }
    } catch (err) {
      console.error("Task completion failed:", err);
      this._showXpToast("Error completing task");
    }
  }

  // ===== INSIGHTS =====

  /**
   * Update insights panel
   */
  updateInsights(insights) {
    // Update percentile
    const percentileEl = document.querySelector(".big-stat");
    if (percentileEl) {
      const percent = insights.percentile || 0;
      percentileEl.textContent = `Top ${percent}%`;
    }

    // Update recommendations
    const insightsContainer = document.querySelector(".insights-container");
    if (insightsContainer && insights.recommendations) {
      const recCards = insightsContainer.querySelectorAll(".insight-card");
      insights.recommendations.forEach((rec, idx) => {
        if (recCards[idx]) {
          recCards[idx].textContent = rec.text;
        }
      });
    }
  }

  // ===== UTILITIES =====

  /**
   * Show XP toast notification
   */
  _showXpToast(msg) {
    const toast = document.getElementById("xpToast");
    if (toast) {
      toast.textContent = msg;
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 3000);
    }
  }

  /**
   * Cache DOM element for performance
   */
  _getCachedElement(selector) {
    if (!this.cache[selector]) {
      this.cache[selector] = document.querySelector(selector);
    }
    return this.cache[selector];
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  if (window.appState) {
    window.uiRenderer = new UIRenderer(window.appState);
    console.log("✓ UI Renderer attached to DOM");
  }
});
