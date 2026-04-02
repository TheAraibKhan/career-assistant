# CareerAssist Full-Stack System Architecture

## 🏗️ System Overview

The application has been upgraded from a static demo to a fully dynamic, data-driven system using a centralized state manager pattern.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React-like)                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  AppState (Single Source of Truth)                 │ │
│  │  • Stores: User, Profile, Skills, Tasks, Stats    │ │
│  │  • Syncs with localStorage on every change        │ │
│  │  • Notifies listeners of state changes            │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  UIRenderer (Event-driven updates)                │ │
│  │  • Listens to all state changes                    │ │
│  │  • Re-renders only affected UI sections           │ │
│  │  • Animates stat card updates                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         ↕ (REST API calls)
┌─────────────────────────────────────────────────────────┐
│                  Backend (Flask)                        │
│  /api/app-state          → Get full app state on load │
│  /api/onboarding         → Save user onboarding data  │
│  /api/task-complete      → Record task completion     │
│  /api/tasks              → Generate daily tasks      │
│  /api/roadmap            → Get personalized roadmap  │
│  /api/journey            → Get phase-specific paths  │
│  /api/user-stats         → Get user statistics      │
│  /api/insights          → Get computed insights     │
└─────────────────────────────────────────────────────────┘
         ↕ (SQL queries)
┌─────────────────────────────────────────────────────────┐
│              Database (SQLite)                          │
│  • user_profiles  → Onboarding data (skills, goals)   │
│  • user_stats     → Aggregate stats (XP, readiness)   │
│  • activity_log   → Activity audit trail              │
│  • task_completion → Per-task tracking               │
│  • skill_progress  → Skill-specific progress        │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 State Manager (`app-state.js`)

Entry point: `window.appState`

### State Structure

```javascript
{
  user: {
    name: string,
    email: string,
    phase: 'pre-college' | 'college' | 'post-college',
    createdAt: ISO timestamp
  },

  profile: {
    skills: [], // ["Python", "React", ...]
    interests: [],
    goals: [],
    daily_time: number // 1-8 hours
  },

  stats: {
    total_xp: number,
    career_readiness: 0-100,
    tasks_completed: number,
    current_streak: number,
    last_activity: ISO timestamp
  },

  skills: {
    "Python": {
      level: 0-5,
      tasksCompleted: number,
      totalXp: number
    },
    ... // one per skill
  },

  roadmap: {
    items: [{
      title, description, status, progress, xp
    }]
  }
}
```

### Key Methods

#### 1. Initialization

```javascript
// After onboarding
appState.initializeProfile({
  name: "User Name",
  phase: "college",
  skills: ["Python", "JavaScript"],
  interests: ["Web Dev", "AI/ML"],
  goals: ["Get internship"],
  daily_time: 3,
});
```

#### 2. Task Completion

```javascript
// When user completes a task
appState.completeTask("Learn React Hooks", 50, "React");
// Auto-updates: XP, tasks, readiness, streak
```

#### 3. Real-time Updates

All state changes automatically:

- Persist to localStorage
- Trigger UI re-renders
- Animate stat card updates
- Recalculate readiness score

#### 4. Computed Values

```javascript
appState.computeInsights();
// Calculates:
// - Percentile ranking
// - Skill growth curves
// - Next milestone XP needed
// - Personalized recommendations
```

---

## 🎨 UI Renderer (`ui-renderer.js`)

Entry point: `window.uiRenderer`

### Auto-Update Sections

1. **Stat Cards**
   - Career Readiness %
   - XP Earned
   - Skills Tracked
   - Tasks Done Today
   - _Animation on change_

2. **Progress Ring**
   - SVG stroke-dashoffset animation
   - Real-time readiness visualization

3. **Skill Tree**
   - Dynamic skill node generation
   - Progress bars per skill
   - Level indicators (Beginner/Intermediate/Advanced)

4. **Roadmap Timeline**
   - Milestone status (locked → active → completed)
   - Dynamic badge text with progress %

5. **Task List**
   - Dynamic task generation from API
   - Click-to-complete with instant updates
   - XP toasts on completion

6. **Insights Panel**
   - Percentile ranking
   - Personalized recommendations
   - Streak tracking display

### Event-Driven Architecture

```javascript
// Subscribe to all state changes
appState.subscribe((prevState, newState) => {
  // Renderer compares and re-renders only changed sections
  if (prevState.stats !== newState.stats) {
    uiRenderer.updateStatCards(newState.stats);
    uiRenderer.updateProgressRing(newState.stats);
  }

  if (prevState.skills !== newState.skills) {
    uiRenderer.updateSkillTree(newState.skills);
  }

  // ... etc
});
```

---

## 🧮 Career Readiness Formula

**Calculated as:**

```
readiness = BASE + SKILLS_SCORE + TASKS_SCORE + STREAK_SCORE
          = 10% + (skills*15) + (tasks*5) + (streak*2)

capped at 95%
```

**Components:**

- **BASE (10%)**: Just from having a profile
- **SKILLS (max 30%)**: Each skill tracked adds 15 points
- **TASKS (max 40%)**: Each task completed adds 5 points
- **STREAK (max 20%)**: Each consecutive day adds 2 points

**Example:**

- 3 skills tracked = 45 points... _capped at 30_
- 5 tasks completed = 25 points
- 7-day streak = 14 points
- **Total: 10 + 30 + 25 + 14 = 79%**

---

## 📝 Streak System

**How it works:**

1. User completes first task today
   → streak = 1, last_activity = today

2. User completes a task tomorrow
   → Is tomorrow the day after last_activity? YES
   → streak = 2

3. User misses a day, completes task 2 days later
   → Is the gap > 1 day? YES
   → streak = 1 (reset)

4. User completes another task same day
   → Has streak already incremented today? YES
   → streak unchanged

**Database:**

```sql
user_stats.current_streak          -- current streak count
user_stats.last_activity_date      -- last day activity occurred (YYYY-MM-DD)
```

---

## 🎯 Task System

### Generation Logic

Tasks are generated based on:

- **daily_time**: How many hours user commits
- **phase**: Different task types per phase
- **goals**: Personalized to user's objectives

**Formula:**

```
num_tasks = max(2, min(5, daily_time / 1))
```

- 1-2 hours = 2 tasks
- 3-4 hours = 3 tasks
- 5+ hours = 5 tasks (max)

### Task Completion Flow

```javascript
1. User clicks task
  ↓
2. Frontend calls POST /api/task-complete
  ├─ task title, XP value, skill
  ↓
3. Backend:
  ├─ Logs to activity_log table
  ├─ Updates user_stats (XP, tasks_completed)
  ├─ Recalculates readiness
  ├─ Checks/updates streak
  ├─ Returns updated stats
  ↓
4. Frontend:
  ├─ appState.setState() updates state
  ├─ Listeners fire → UI auto-updates
  ├─ Animations play
  ├─ XP toast shows
  ↓
5. localStorage syncs automatically
```

---

## 🗺️ Roadmap System

### Milestone Status Flow

```
Phase 1: Locked  → Phase 2: Locked
                       ↓
                   Locked → Active → Completed → Locked
                   (start phase)   (10 tasks)   (next milestone)
```

### Dynamic Updates

Milestones are generated from:

- User's primary skill (determines which roadmap)
- Phase-specific progression (3 tiers per phase)
- Personalized titles/descriptions

**Example for Python track:**

1. Python Fundamentals (In Progress - Week 1/4)
2. Data Structures with Python (Locked)
3. Web Backend with Flask/Django (Locked)

---

## 🎓 Skill Tracking

### Skill Object

```javascript
skills["Python"] = {
  level: 0, // 0-5 (beginner to expert)
  tasksCompleted: 5, // number of tasks
  totalXp: 250, // aggregate XP for this skill
  progress: 50, // % toward next level
};
```

### Level Calculation

```
level = totalXp / 500    // Every 500 XP = +1 level

level 0-1 = "Beginner"
level 2-3 = "Intermediate"
level 4+  = "Advanced"
```

### Progress Bar

```
progress% = (totalXp % 500) / 5
```

Shows % progress to next level

---

## 🔄 Data Flow on Task Completion

### Frontend

```javascript
// app-state.js
completeTask(title, xp, skill) {
  // 1. Update stats
  stats.total_xp += xp
  stats.tasks_completed += 1

  // 2. Update skill
  skills[skill].totalXp += xp
  skills[skill].tasksCompleted += 1

  // 3. Check streak
  if (isConsecutiveDay()) {
    stats.current_streak += 1
  } else {
    stats.current_streak = 1
  }

  // 4. Recalculate readiness
  stats.career_readiness = calculateReadiness(stats)

  // 5. Trigger state change
  setState({ stats, skills })
  // ↓ Automatically triggers UIRenderer listeners
}
```

### Backend

```python
# routes/career_ai_routes.py
@app.post('/api/task-complete')
def complete_task():
  # 1. Create tables if needed
  # 2. Insert into activity_log
  # 3. Get or create user_stats row
  # 4. Update total_xp, tasks_completed, current_streak
  # 5. Recalculate career_readiness
  # 6. Return updated stats JSON
  return {
    'success': True,
    'stats': {
      'total_xp': 250,
      'tasks_completed': 5,
      'career_readiness': 45,
      'current_streak': 3
    }
  }
```

### Database

```sql
INSERT INTO activity_log
  (user_id, activity_type, task_title, xp_earned, created_at)
  VALUES (?, 'task_complete', ?, ?, now)

UPDATE user_stats
  SET total_xp = 250, tasks_completed = 5,
      career_readiness = 45, current_streak = 3
  WHERE user_id = ?
```

---

## 🌐 API Endpoints

### `/api/app-state` (GET)

**Returns:** Complete app state for initialization

```json
{
  "success": true,
  "appState": {
    "user": { ... },
    "profile": { ... },
    "stats": { ... },
    "skills": { ... },
    "roadmap": { ... }
  }
}
```

### `/api/onboarding` (POST/GET)

**POST:** Save user onboarding profile

```json
POST /api/onboarding
{
  "skills": ["Python", "React"],
  "interests": ["Web Dev"],
  "phase": "college",
  "goals": ["Get internship"],
  "daily_time": 3
}

Response:
{
  "success": true,
  "message": "Profile saved"
}
```

**GET:** Retrieve user's onboarding profile (returns same structure)

### `/api/task-complete` (POST)

**Payload:**

```json
{
  "title": "Learn React Hooks",
  "xp": 50,
  "skill": "React"
}
```

**Response:**

```json
{
  "success": true,
  "stats": {
    "total_xp": 250,
    "tasks_completed": 5,
    "career_readiness": 45,
    "current_streak": 3
  }
}
```

### `/api/tasks` (GET)

**Returns:** Array of daily tasks

```json
{
  "success": true,
  "tasks": [
    {
      "title": "Practice Python fundamentals",
      "category": "Practice",
      "duration": "30 mins",
      "xp": 50,
      "skill": "Python"
    },
    ...
  ]
}
```

### `/api/roadmap` (GET)

**Returns:** User's personalized roadmap

```json
{
  "success": true,
  "roadmap": [
    {
      "title": "Python Fundamentals",
      "description": "Variables, loops, functions",
      "duration": "4 weeks",
      "xp": 200,
      "status": "In Progress"
    },
    ...
  ]
}
```

### `/api/journey` (GET)

**Returns:** Phase-specific milestones

```json
{
  "success": true,
  "journey": [
    {
      "title": "Discover Your Interests",
      "description": "Take aptitude tests...",
      "xp": 100,
      "status": "In Progress"
    },
    ...
  ]
}
```

---

## 📱 UI/UX Patterns

### Real-time Stat Updates

1. User clicks task
2. XP toast appears: `+50 XP Earned! ⚡`
3. Stat cards fade and scale briefly
4. Numbers update with animation
5. Progress ring animates new offset
6. All within 300ms

### Streak Display

- Shows current streak day count
- Calendar strip shows each day (7 days visible)
- Active days highlighted
- Today always marked

### Skill Progress

- Icon + skill name
- Horizontal progress bar
- Level badge (Beginner/Intermediate/Advanced)
- Tooltip shows next level XP needed

### Roadmap Milestones

- Completed milestones: Green checkmark with "✓"
- Active milestone: Blue play button with "▶"
- Locked milestones: Gray dash with "—"
- Badge shows: completion % or unlock condition

---

## 📊 Test Cases

### Test 1: Onboarding to Dashboard

```
1. Visit /app (not logged in or new user)
2. See onboarding modal
3. Fill out: 3 skills, 1 interest, 1 goal, phase, daily_time
4. Click "Get Roadmap"
5. Modal closes, dashboard appears
6. Stats show 0% readiness, 0 XP, tasks loaded
✓ Check localStorage has state
✓ Refresh page - state persists
```

### Test 2: Task Completion

```
1. From dashboard, click "Practice Python"
2. Task marks done, XP toast appears
3. "Career Readiness" stat updates: 0% → 15%
4. "XP Earned" updates: 0 → 50
5. "Tasks Done Today" updates: 0/5 → 1/5
✓ Refresh page - stats persist
```

### Test 3: Streak Tracking

```
Day 1:
1. Complete any task
2. Stats show: streak = 1

Day 2:
1. Complete any task
2. Stats show: streak = 2

Skip Day 3, then Day 4:
1. Complete task
2. Stats show: streak = 1 (reset)
```

### Test 4: Skill Progress

```
1. From task: "Learn React Hooks" (+React, +50 XP)
2. Complete same task 3x (150 XP total)
3. React skill shows: "Beginner" (0 XP)
   (needs 500 XP for next level)
4. Progress bar: 150/500 = 30%
```

### Test 5: Readiness Calculation

```
Initial: 10%
+ 3 skills tracked: 10 + 45 (capped 30) = 40%
+ 5 tasks completed: 40 + 25 = 65%
+ 7-day streak: 65 + 14 = 79%
✓ Verify calculation in network tab
```

---

## 🔧 Developer Console

Open DevTools (F12) to inspect:

```javascript
// View current state
window.appState.debug();

// View listener count
window.appState.listeners.length;

// View stored localStorage
localStorage.getItem("careerAssist_state");

// Get current stats
window.appState.state.stats;

// Get current skills
window.appState.state.skills;

// Clear state (dev only)
window.appState.reset();

// Check UI renderer
window.uiRenderer;
```

---

## 📚 Architecture Benefits

✅ **Single Source of Truth**: AppState is the only place data lives
✅ **Real-time Updates**: UI automatically re-renders on any change
✅ **Persistence**: localStorage syncs automatically, survives refresh
✅ **Scalability**: Adding new UI sections is just a listener callback
✅ **Testability**: State is pure, predictable, easy to test
✅ **Performance**: Only changed sections re-render (not entire page)
✅ **Offline Ready**: Works without internet (uses localStorage)
✅ **Time-travel**: Every state change is logged, can be replayed

---

## 🚀 Future Enhancements

1. **Phase-based Task Recommendations**
   - Different task pools per phase
   - Auto-difficulty scaling

2. **Project Management**
   - Start/track projects
   - Link tasks to projects
   - Portfolio export

3. **Multiplayer Features**
   - Leaderboards (by percentile)
   - Study groups
   - Mentor matching

4. **ML Features**
   - Skill gap analysis from resume
   - Job match scoring
   - Personalized learning paths

5. **Mobile App**
   - React Native using same state manager
   - Push notifications for daily reminders
   - Offline task syncing
