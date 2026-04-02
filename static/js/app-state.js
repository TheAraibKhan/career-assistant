/**
 * CareerAssist App State Manager
 * Single source of truth for all application state
 * Syncs with localStorage for persistence
 */

class AppState {
  constructor() {
    this.state = {
      // User profile from onboarding
      user: {
        name: "",
        email: "",
        phase: "", // pre-college, college, post-college
        createdAt: null,
      },

      // Onboarding selections
      profile: {
        skills: [], // user selected skills
        interests: [], // user interests
        goals: [], // career goals
        daily_time: 1, // hours per day
      },

      // Core metrics
      stats: {
        total_xp: 0,
        career_readiness: 0, // calculated value
        tasks_completed: 0,
        current_streak: 0,
        last_activity: null, // timestamp
      },

      // Skills tracking
      skills: {}, // { skillName: { level: 0-100, tasksCompleted: N, totalXp: N } }

      // Daily task tracking
      tasks: {
        current_day: null, // YYYY-MM-DD
        completed_today: 0,
        all_completed: [], // list of { title, xp, completedAt }
      },

      // Roadmap/Milestones
      roadmap: {
        items: [], // { title, status: 'locked|active|completed', xp, progress }
      },

      // Projects
      projects: {
        active: [], // projects user is working on
        completed: [], // projects finished
      },

      // Insight calculations
      insights: {
        skill_growth: {}, // { skillName: percentileRank }
        percentile: 0, // where user ranks (0-100)
        next_milestone_xp: 0, // XP needed for next level
        recommendations: [],
      },
    };

    this.listeners = []; // state change watchers
    this.loadFromStorage();
  }

  /**
   * Load state from localStorage
   */
  loadFromStorage() {
    try {
      const stored = localStorage.getItem("careerAssist_state");
      if (stored) {
        const parsed = JSON.parse(stored);
        this.state = { ...this.state, ...parsed };
        console.log("✓ State loaded from localStorage");
      } else {
        console.log("ℹ No state in localStorage, starting fresh");
      }
    } catch (e) {
      console.warn("Failed to load state:", e);
    }
  }

  /**
   * Save state to localStorage
   */
  saveToStorage() {
    try {
      localStorage.setItem("careerAssist_state", JSON.stringify(this.state));
    } catch (e) {
      console.warn("Failed to save state:", e);
    }
  }

  /**
   * Get current state (immutable reference)
   */
  getState() {
    return { ...this.state };
  }

  /**
   * Update state and trigger listeners
   */
  setState(updates) {
    const prevState = { ...this.state };
    this.state = { ...this.state, ...updates };
    this.saveToStorage();
    this.notifyListeners(prevState, this.state);
    return this.state;
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener) {
    this.listeners.push(listener);
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  /**
   * Notify all state watchers
   */
  notifyListeners(prevState, newState) {
    this.listeners.forEach((listener) => {
      try {
        listener(prevState, newState);
      } catch (e) {
        console.error("State listener error:", e);
      }
    });
  }

  // ===== PROFILE METHODS =====

  /**
   * Initialize user profile from onboarding
   */
  initializeProfile(onboardingData) {
    console.log("Initializing profile:", onboardingData);

    const updated = {
      user: {
        ...this.state.user,
        name: onboardingData.name || "Profile",
        email: onboardingData.email || "",
        phase: onboardingData.phase || "college",
        createdAt: new Date().toISOString(),
      },
      profile: {
        skills: Array.isArray(onboardingData.skills)
          ? onboardingData.skills
          : [],
        interests: Array.isArray(onboardingData.interests)
          ? onboardingData.interests
          : [],
        goals: Array.isArray(onboardingData.goals) ? onboardingData.goals : [],
        daily_time: onboardingData.daily_time || 1,
      },
    };

    // Initialize skills object
    const skillsObj = {};
    updated.profile.skills.forEach((skill) => {
      skillsObj[skill] = {
        level: 0,
        tasksCompleted: 0,
        totalXp: 0,
      };
    });
    updated.skills = skillsObj;

    return this.setState(updated);
  }

  // ===== TASK METHODS =====

  /**
   * Complete a task and update all related metrics
   */
  completeTask(taskTitle, xp, skill = null) {
    console.log(`Completing task: "${taskTitle}" (+${xp} XP)`);

    const updatedStats = { ...this.state.stats };
    updatedStats.total_xp += xp;
    updatedStats.tasks_completed += 1;

    // Update skill if provided
    const updatedSkills = { ...this.state.skills };
    if (skill && updatedSkills[skill]) {
      updatedSkills[skill].tasksCompleted += 1;
      updatedSkills[skill].totalXp += xp;
    }

    // Check if streak should be updated
    const today = new Date().toISOString().split("T")[0];
    let updatedStreak = this.state.stats.current_streak;
    const lastActivity = this.state.stats.last_activity;

    if (lastActivity) {
      const lastDate = lastActivity.split("T")[0];
      if (lastDate === today) {
        // Already completed a task today
        updatedStreak = this.state.stats.current_streak;
      } else if (this._isConsecutiveDay(lastDate, today)) {
        // Consecutive day
        updatedStreak = this.state.stats.current_streak + 1;
      } else {
        // Streak broken, reset to 1
        updatedStreak = 1;
      }
    } else {
      // First task ever
      updatedStreak = 1;
    }

    updatedStats.current_streak = updatedStreak;
    updatedStats.last_activity = new Date().toISOString();

    // Recalculate career readiness
    updatedStats.career_readiness = this._calculateReadiness(
      updatedStats,
      updatedSkills,
    );

    return this.setState({
      stats: updatedStats,
      skills: updatedSkills,
    });
  }

  // ===== CALCULATION METHODS =====

  /**
   * Calculate career readiness score (0-100)
   * Formula: (skills_count * 20) + (tasks_completed * 5) + (streak * 2) capped at 95
   */
  _calculateReadiness(stats, skills) {
    const skillsCount = Object.keys(skills).length;
    const skillsScore = Math.min(skillsCount * 15, 30); // Max 30 points
    const tasksScore = Math.min(stats.tasks_completed * 5, 40); // Max 40 points
    const streakScore = Math.min(stats.current_streak * 2, 20); // Max 20 points
    const baseScore = 10; // Base 10% for existing

    const total = baseScore + skillsScore + tasksScore + streakScore;
    return Math.min(total, 95); // Cap at 95%
  }

  /**
   * Check if two dates are consecutive days
   */
  _isConsecutiveDay(prevDate, currentDate) {
    const prev = new Date(prevDate);
    const curr = new Date(currentDate);
    const dayMs = 24 * 60 * 60 * 1000;
    return curr - prev === dayMs;
  }

  /**
   * Calculate which percentile user is in
   */
  _calculatePercentile(stats, skills) {
    const totalScore =
      stats.total_xp + stats.tasks_completed * 100 + stats.current_streak * 50;
    // Simple percentile: assume avg user has 500 score, max is 2000
    return Math.min(100, Math.round((totalScore / 2000) * 100));
  }

  /**
   * Get next level milestone
   */
  _getNextMilestone(stats) {
    const levelThresholds = [500, 1000, 2000, 3500, 5000];
    for (const threshold of levelThresholds) {
      if (stats.total_xp < threshold) {
        return {
          xp_needed: threshold - stats.total_xp,
          level: levelThresholds.indexOf(threshold) + 1,
        };
      }
    }
    return { xp_needed: 0, level: 6 };
  }

  // ===== SKILL METHODS =====

  /**
   * Update skill progress
   */
  updateSkillProgress(skillName, xpGained) {
    const updated = { ...this.state.skills };
    if (updated[skillName]) {
      updated[skillName].totalXp += xpGained;
      // Level up: rough estimate (every 500 XP = +1 level)
      updated[skillName].level = Math.floor(updated[skillName].totalXp / 500);
    }
    return this.setState({ skills: updated });
  }

  /**
   * Get all skills with computed levels
   */
  getSkillsWithLevels() {
    const skillLevels = {};
    Object.entries(this.state.skills).forEach(([name, data]) => {
      const level = data.level || 0;
      let proficiency = "Beginner";
      if (level >= 3) proficiency = "Advanced";
      else if (level >= 2) proficiency = "Intermediate";

      skillLevels[name] = {
        ...data,
        proficiency,
        progress: Math.min(100, (data.totalXp % 500) / 5), // 0-100% to next level
      };
    });
    return skillLevels;
  }

  // ===== ROADMAP METHODS =====

  /**
   * Update roadmap from API
   */
  setRoadmap(roadmapItems) {
    const updated = roadmapItems.map((item, idx) => ({
      ...item,
      id: idx,
      status: idx === 0 ? "completed" : idx === 1 ? "active" : "locked",
      progress: idx === 0 ? 100 : idx === 1 ? 30 : 0,
    }));

    return this.setState({
      roadmap: { items: updated },
    });
  }

  // ===== INSIGHTS METHODS =====

  /**
   * Compute all insights
   */
  computeInsights() {
    const insights = {
      percentile: this._calculatePercentile(
        this.state.stats,
        this.state.skills,
      ),
      skill_growth: this._computeSkillGrowth(),
      next_milestone: this._getNextMilestone(this.state.stats),
      recommendations: this._generateRecommendations(),
    };

    return this.setState({ insights });
  }

  /**
   * Compute growth for each skill
   */
  _computeSkillGrowth() {
    const growth = {};
    Object.entries(this.state.skills).forEach(([name, data]) => {
      // Rough percentile: 0 = beginner, 50 = intermediate, 100 = expert
      growth[name] = Math.min(100, data.level * 20);
    });
    return growth;
  }

  /**
   * Generate recommendations based on progress
   */
  _generateRecommendations() {
    const recs = [];
    const { stats, profile } = this.state;

    // Recommendation 1: Streak
    if (stats.current_streak < 7) {
      recs.push({
        type: "streak",
        text: `You're on a ${stats.current_streak}-day streak. Go for 7!`,
        priority: "high",
      });
    }

    // Recommendation 2: Skills
    if (Object.keys(this.state.skills).length < 3) {
      recs.push({
        type: "skills",
        text: `You have ${Object.keys(this.state.skills).length} skills tracked. Diversify to ${profile.skills.length}!`,
        priority: "medium",
      });
    }

    // Recommendation 3: XP milestone
    if (stats.total_xp < 500) {
      recs.push({
        type: "xp",
        text: `Complete ${Math.ceil((500 - stats.total_xp) / 50)} more tasks to hit 500 XP!`,
        priority: "medium",
      });
    }

    // Recommendation 4: Phase-specific
    if (profile.phase === "college" && stats.tasks_completed < 5) {
      recs.push({
        type: "phase",
        text: "College phase: Focus on projects. Build 1 portfolio piece this month.",
        priority: "high",
      });
    }

    return recs;
  }

  // ===== DEBUG METHODS =====

  /**
   * Log full state to console
   */
  debug() {
    console.table(this.state);
    return this.state;
  }

  /**
   * Reset state completely (dev only)
   */
  reset() {
    localStorage.removeItem("careerAssist_state");
    location.reload();
  }
}

// Create global instance
window.appState = new AppState();
console.log("✓ App State Manager initialized");
