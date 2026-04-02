# Dashboard Data Architecture - Real vs. Dummy

## Current Status

### ✅ REAL DATA (From User)

These are genuine and come directly from the user's input:

1. **User's Name** - From `users.full_name`
2. **User's Skills** - From `user_profiles.skills` (onboarding)
3. **User's Interests** - From `user_profiles.interests` (onboarding)
4. **User's Phase** - From `user_profiles.phase` (pre-college, college, post-college)
5. **User's Goals** - From `user_profiles.goals` (onboarding)
6. **User's Daily Time** - From `user_profiles.daily_time` (onboarding)

### ❌ DUMMY DATA (Hardcoded Placeholders)

These are currently hardcoded/placeholder and need activity tracking:

1. **68% Career Readiness** - Currently static, should be calculated from user's progress
2. **1,240 XP Earned** - Dummy, needs activity tracking
3. **8 Skills Tracked** - Dummy static count
4. **3/5 Tasks Done Today** - Dummy counter
5. **7-Day Streak** - Dummy, needs activity tracking
6. **Roadmap Items** - Now REAL! Generated based on user's primary skill
7. **Journey/Milestones** - Now REAL! Generated based on user's phase
8. **Daily Tasks** - Now REAL! Generated based on daily_time and goals
9. **Insights/Analytics** - Now REAL! Generated based on onboarding data
10. **Skill Growth Charts** - Currently placeholder, will use activity data

---

## New APIs Available

All these endpoints are NOW AVAILABLE and return REAL, PERSONALIZED DATA:

### 1. **`/api/roadmap` [GET]**

**Purpose:** Get personalized learning roadmap based on user's primary skill  
**Returns:** List of milestone courses tailored to skill (Python → Python Fundamentals → Data Structures → Web Backend)  
**Example Response:**

```json
{
  "success": true,
  "roadmap": [
    {
      "title": "Python Fundamentals",
      "description": "Variables, loops, functions, OOP concepts, file handling.",
      "duration": "4 weeks",
      "xp": 200,
      "status": "In Progress"
    }
  ]
}
```

### 2. **`/api/tasks` [GET]**

**Purpose:** Generate daily tasks based on user's daily_time commitment and goals  
**Returns:** 2-5 tasks per day (based on `daily_time` input, 1-8 hours)  
**Example Response:**

```json
{
  "success": true,
  "tasks": [
    {
      "title": "Practice Python fundamentals",
      "description": "Complete coding exercises in Python.",
      "duration": "30 mins",
      "xp": 50,
      "priority": "high",
      "category": "Practice"
    }
  ]
}
```

### 3. **`/api/journey` [GET]**

**Purpose:** Get phase-specific milestones and career journey  
**Returns:** 4 major milestones based on user's phase (pre-college vs college vs post-college)  
**Phase Milestones:**

- **Pre-College:** Discover → Learn Basics → Build First Project → Explore Paths
- **College:** Master Core → Portfolio Projects → Interview Prep → Land Internship
- **Post-College:** Specialize → Lead Projects → Personal Brand → Senior Level

**Example Response:**

```json
{
  "success": true,
  "journey": [
    {
      "title": "Master Core Skills",
      "description": "Deepen knowledge in chosen domain.",
      "xp": 300,
      "status": "In Progress"
    }
  ]
}
```

### 4. **`/api/stats` [GET]**

**Purpose:** Get user's current statistics  
**Returns:** XP, streak, tasks done, career readiness, skills tracked  
**Note:** Currently returns 0 for new users. Will track from activity in future.  
**Example Response:**

```json
{
  "success": true,
  "stats": {
    "xp": 0,
    "streak": 0,
    "tasks_done": 0,
    "career_readiness": 0,
    "skills_tracked": 1
  }
}
```

### 5. **`/api/insights` [GET]**

**Purpose:** Get analytics and personalized recommendations  
**Returns:** Skill growth, activity heatmap, AI recommendations based on goals  
**Example Response:**

```json
{
  "success": true,
  "insights": {
    "skill_growth": {
      "Python": { "level": "Beginner", "progress": 15, "trend": "up" }
    },
    "recommendations": [
      "Focus on DSA and system design for job interviews",
      "Build 2-3 portfolio projects to attract recruiters"
    ]
  }
}
```

---

## How to Use These APIs in Frontend

The dashboard already has the API calls implemented! In `applyProfile()` function:

```javascript
async function loadRealDashboardData() {
  // Load roadmap based on skills
  const roadmapRes = await fetch("/api/roadmap");
  const roadmapData = await roadmapRes.json();

  // Load tasks based on daily_time
  const tasksRes = await fetch("/api/tasks");
  const tasksData = await tasksRes.json();

  // Load journey based on phase
  const journeyRes = await fetch("/api/journey");
  const journeyData = await journeyRes.json();

  // Load stats (XP, streak, etc.)
  const statsRes = await fetch("/api/stats");
  const statsData = await statsRes.json();

  // Load insights
  const insightsRes = await fetch("/api/insights");
  const insightsData = await insightsRes.json();
}
```

---

## What Still Needs Activity Tracking

To make these fully real (not just personalized), we need activity tracking:

### Database Table Needed: `user_stats`

```sql
CREATE TABLE user_stats (
  id INTEGER PRIMARY KEY,
  user_id TEXT UNIQUE NOT NULL,
  total_xp INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  tasks_completed INTEGER DEFAULT 0,
  skills_tracked INTEGER DEFAULT 1,
  career_readiness INTEGER DEFAULT 0,
  last_activity_date TEXT,
  created_at TEXT,
  updated_at TEXT
);
```

### User Actions to Track

1. ✅ Task Completion → +XP
2. ✅ Daily Consistency → Streak counter
3. ✅ Skill Progress → Update readiness %
4. ✅ Millstone Completion → Level up

### Activity Events to Log

- When user completes a task
- When user marks task as done (toggleTask)
- When user completes a milestone
- Daily active check (for streak)

---

## Summary

| Data               | Status      | Source                   |
| ------------------ | ----------- | ------------------------ |
| User Name          | ✅ REAL     | users.full_name          |
| Skills             | ✅ REAL     | user_profiles.skills     |
| Interests          | ✅ REAL     | user_profiles.interests  |
| Phase              | ✅ REAL     | user_profiles.phase      |
| Goals              | ✅ REAL     | user_profiles.goals      |
| Daily Time         | ✅ REAL     | user_profiles.daily_time |
| Roadmap            | ✅ REAL NOW | `GET /api/roadmap`       |
| Daily Tasks        | ✅ REAL NOW | `GET /api/tasks`         |
| Journey            | ✅ REAL NOW | `GET /api/journey`       |
| Insights           | ✅ REAL NOW | `GET /api/insights`      |
| Stats (XP, Streak) | ⏳ PENDING  | Needs activity tracking  |
| Career Readiness % | ⏳ PENDING  | Needs activity tracking  |

---

## Next Steps

1. **Implement Activity Tracking**
   - Create `user_stats` table
   - Log events when users complete tasks
   - Update stats in real-time

2. **Connect Frontend to APIs**
   - Populate dashboard sections with API responses
   - Replace dummy hardcoded data with API data

3. **Gamification Elements**
   - XP system for task completion
   - Streak rewards
   - Achievement badges
   - Leaderboard

4. **Analytics Dashboard**
   - Activity heatmap
   - Skill progress charts
   - Recommendations engine
