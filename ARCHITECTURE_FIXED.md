# CareerAssist - Unified Data Architecture

## Overview

This document describes the fixed architecture that ensures CareerAssist behaves like a unified system that understands the user once and reflects that understanding everywhere.

## Single Source of Truth: Profile Service

The `profile_service.py` is the authoritative source for all user data. Every module must consume data through this service.

### Profile Service API

```python
from services.profile_service import get_user_profile, update_user_profile

# Reading user data (used by all modules)
profile = get_user_profile(user_id)
# Returns:
# {
#   'user': {'id', 'name', 'email', 'phase', 'created_at'},
#   'profile': {'skills', 'interests', 'goals', 'daily_time', 'primary_skill', 'completed'},
#   'stats': {'total_xp', 'tasks_completed', 'career_readiness', 'current_streak', 'skills_tracked'},
#   'skills': {'skill_name': {'level', 'tasksCompleted', 'totalXp'}},
#   'resume_data': {'ats_score', 'overall_score', 'skills_found', 'recommendations'}
# }

# Writing user data (single point of update)
updated_profile = update_user_profile(user_id, {
    'skills': ['Python', 'JavaScript'],
    'interests': ['Web Dev', 'Startups'],
    'phase': 'college',
    'goals': ['Get a job', 'Build portfolio'],
    'daily_time': 2
})
```

## Data Flow Architecture

### 1. User Input → Database

- **Dashboard Onboarding**: User enters skills, interests, goals, phase, daily_time
- **Route**: `/api/onboarding` (POST)
- **Handler**: `save_onboarding()` in career_ai_routes.py
- **Action**: Calls `profile_service.update_user_profile()`
- **Result**: All user data stored in `user_profiles` table, stats initialized in `user_stats`, skill_progress records created

### 2. Database → Unified Profile

- **Entry Point**: `profile_service.get_user_profile(user_id)`
- **Process**:
  1. Fetches user from `users` table
  2. Gets onboarding data from `user_profiles` table
  3. Retrieves stats from `user_stats` table
  4. Gets skill progress from `skill_progress` table
  5. Gets resume data from `quick_analyses` table
- **Output**: Complete profile object

### 3. Profile → All Modules

Each module receives the same profile data:

#### Roadmap Module

```python
# Route: /api/roadmap
profile = get_user_profile(user_id)
roadmap = generate_roadmap(profile['profile'], profile['stats'])
# Uses: skills, goals to generate learning path
```

#### Insights Module

```python
# Route: /api/insights
profile = get_user_profile(user_id)
insights = generate_insights(
    profile_data=profile['profile'],
    stats=profile['stats'],
    skills_data=profile['skills'],
    resume_data=profile.get('resume_data')
)
# Uses: skills, interests, goals to generate insights
```

#### Master Profile API

```python
# Route: /api/user-profile
profile = get_user_profile(user_id)
# Returns complete profile with roadmap, stats, skills, everything
```

## Data Consistency Rules

### ENFORCE:

1. **All reads** come from `profile_service.get_user_profile()`
2. **All writes** go through `profile_service.update_user_profile()`
3. **No module** accesses database directly for user profile data
4. **No hardcoded values** - everything derives from user profile
5. **No independent data sources** - all modules use same base data

### Database Tables

**user_profiles**: Core profile

- user_id (unique)
- skills (JSON)
- interests (JSON)
- phase (string: pre-college, college, post-college)
- goals (JSON)
- daily_time (integer: hours per day)
- created_at, updated_at

**user_stats**: Aggregated progress

- user_id (unique)
- total_xp
- tasks_completed
- career_readiness (0-100)
- current_streak
- skills_tracked (count)
- created_at, updated_at

**skill_progress**: Per-skill tracking

- user_id + skill_name (unique)
- proficiency_level
- tasks_completed
- total_xp

**quick_analyses**: Resume analysis cache

- user_id
- ats_score
- overall_score
- skills_found (JSON)
- recommendations (JSON)

## Module Dependencies

```
User Interface (Dashboard, Onboarding)
    ↓
routes/career_ai_routes.py
    ↓
services/profile_service.py (Single Source of Truth)
    ↓
    ├→ services/roadmap_service.py (uses profile.skills + profile.goals)
    ├→ services/insight_service.py (uses profile + stats + skills)
    ├→ services/auth_service.py (user details)
    └→ database/db.py (persistence)
```

## Update Synchronization

When user profile changes:

1. **Onboarding save** → `update_user_profile()` → Database updated
2. **Next read** → `get_user_profile()` → All modules see new data
3. **Auto-sync**: Roadmap, insights, projects all automatically reflect changes

Example flow when user updates skills:

```
User edits: "Python" → ["Python", "React"]
    ↓
POST /api/onboarding with new skills
    ↓
save_onboarding() calls update_user_profile()
    ↓
Database updated, skill_progress records created for React
    ↓
Next GET /api/roadmap, /api/insights etc get new data
    ↓
All modules show updated roadmap, insights reflecting new skill
```

## Key Improvements

### Before

- Roadmap logic duplicated in routes AND roadmap_service
- Dashboard, roadmap, insights used different data sources
- User data inconsistency across modules
- No sync mechanism when profile updated

### After

✓ Single roadmap logic in roadmap_service
✓ All modules use profile_service
✓ Guaranteed data consistency
✓ Automatic sync on profile update
✓ Clear separation of concerns
✓ Removed AI-looking emojis
✓ Removed hardcoded duplicate data

## Testing Data Flow

```bash
# 1. Create user via signup
# 2. POST /api/onboarding with profile data
curl -X POST http://localhost:5000/api/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python"],
    "interests": ["Web Dev"],
    "phase": "college",
    "goals": ["Get a job"],
    "daily_time": 2
  }'

# 3. Verify data is available across modules
curl http://localhost:5000/api/user-profile      # Complete profile
curl http://localhost:5000/api/roadmap           # Uses skills + goals
curl http://localhost:5000/api/insights          # Uses profile + stats
curl http://localhost:5000/api/onboarding        # Latest profile data
```

## File Changes Summary

### Modified Files

- `services/profile_service.py` - Enhanced with update_user_profile() function
- `routes/career_ai_routes.py` - Removed duplicate roadmap logic, refactored to use profile_service
- `templates/career_ai/*.html` - Removed AI-looking emojis, replaced with text indicators

### Removed

- Duplicate `_get_roadmap_for_user()` function in routes (replaced with roadmap_service)
- Emoji icons from templates (CA, D, J, R, P, RL, I text-based)

## Next Steps

To maintain this architecture:

1. Always call `profile_service.update_user_profile()` when saving profile
2. Always call `profile_service.get_user_profile()` when reading profile
3. Services should accept profile data as parameters, not fetch it themselves
4. Add new features by:
   - Getting profile from profile_service
   - Processing it in appropriate service
   - Never accessing database directly for profile data
