# Quick Reference Guide

## For Developers: Using the New System

### 1. Get a Career Recommendation

```python
from services.recommendation import analyze_profile

# Get role recommendation based on interest + level
result = analyze_profile("ai", "intermediate")

print(result["career"])        # "AI Engineer"
print(result["tier"])          # "intermediate"
print(result["confidence"])    # 80
print(result["next_role"])     # "Senior AI Engineer"
```

### 2. Check Skill Requirements for a Role

```python
from services.skill_gap_advanced import get_skill_gap_advanced

skills = get_skill_gap_advanced("AI Engineer")

print(len(skills["core_skills"]))     # Number of core skills (4+)
print(len(skills["optional_skills"])) # Number of optional skills (1+)

for skill in skills["core_skills"]:
    print(f"{skill['name']}: {skill['weight']}% - {skill['reason']}")
```

### 3. Calculate Readiness Score

```python
from services.readiness_advanced import calculate_readiness_advanced

acquired = ["Python", "Machine Learning", "Statistics"]
readiness = calculate_readiness_advanced("AI Engineer", acquired)

print(f"Score: {readiness['readiness_score']}%")
print(f"Matched: {len(readiness['strengths'])} skills")
print(f"Missing: {len(readiness['gaps'])} skills")
print(f"Critical Gaps: {len(readiness['missing_core_skills'])}")

for action in readiness['next_actions']:
    print(f"- {action}")
```

### 4. Save Analysis to Database

```python
from database.models import insert_log
import json

submission_id = insert_log(
    name="John Doe",
    interest="tech",
    level="beginner",
    recommendation="Junior Developer",
    known_skills="JavaScript, HTML, CSS",
    readiness_score=45,
    confidence_score=70,
    recommended_role_tier="beginner",
    strengths=json.dumps(["JavaScript", "HTML"]),
    gaps=json.dumps(["Backend", "Databases"])
)

print(f"Saved as ID: {submission_id}")
```

### 5. Fetch All Submissions (Admin)

```python
from database.models import fetch_all_logs

all_submissions = fetch_all_logs()
for submission in all_submissions:
    print(f"{submission['name']} → {submission['recommendation']}")
```

---

## API Endpoints

### GET /

Display the career assistant form

**Parameters:** None
**Returns:** HTML form

### POST /

Process form submission

**Form Parameters:**

- `name` (string) - User name
- `interest` (select) - ai, tech, data, design, business
- `level` (select) - beginner, junior, intermediate, advanced, expert
- `known_skills` (multi-select) - List of skill names

**Returns:** HTML page with results:

```html
- recommendation (str) - confidence (int) - readiness_score (int) - strengths
(list of dicts) - gaps (list of dicts) - next_actions (list of str) - next_role
(str) - missing_skills (list of str) - roadmap (list of str) - user_name (str) -
error (str if error occurred)
```

### GET /admin/

Admin dashboard (requires login)

**Parameters:** None
**Returns:** Dashboard with submission stats

### POST /admin/login

Admin login

**Form Parameters:**

- `username` (string)
- `password` (string)

**Returns:** Redirect to /admin/ if successful

### GET /admin/logout

Admin logout

**Parameters:** None
**Returns:** Redirect to home page

---

## Database Schema

### submissions table

| Column                | Type                | Description                                        |
| --------------------- | ------------------- | -------------------------------------------------- |
| id                    | INTEGER PRIMARY KEY | Auto-incremented ID                                |
| name                  | TEXT NOT NULL       | User's name                                        |
| interest              | TEXT NOT NULL       | Career interest (ai, tech, data, design, business) |
| level                 | TEXT NOT NULL       | Experience level                                   |
| known_skills          | TEXT                | Comma-separated skill list                         |
| recommendation        | TEXT NOT NULL       | Recommended role                                   |
| readiness_score       | INTEGER             | 0-100 readiness percentage                         |
| confidence_score      | INTEGER             | 0-100 confidence percentage                        |
| created_at            | TEXT NOT NULL       | ISO timestamp of submission                        |
| recommended_role_tier | TEXT                | Tier of recommended role                           |
| strengths             | TEXT                | JSON array of matched skills                       |
| gaps                  | TEXT                | JSON array of missing skills                       |

---

## Interest & Level Mappings

### Valid Interests

- `ai` → AI/ML career path
- `tech` → Software Engineering career path
- `data` → Data Science career path
- `design` → UI/UX Design career path
- `business` → Business & Product career path

### Valid Levels

- `beginner` → 0-1 years experience
- `junior` → 1-2 years experience
- `intermediate` → 2-4 years experience
- `advanced` → 4-7 years experience
- `expert` → 7+ years experience

### Role Mappings (Examples)

| Interest | Level        | Role                             |
| -------- | ------------ | -------------------------------- |
| ai       | beginner     | ML Intern                        |
| ai       | junior       | ML Engineer                      |
| ai       | intermediate | AI Engineer                      |
| ai       | advanced     | Senior AI Engineer               |
| ai       | expert       | AI Research Scientist            |
| tech     | beginner     | Junior Developer                 |
| tech     | intermediate | Software Engineer                |
| tech     | advanced     | Senior Software Engineer         |
| tech     | expert       | Staff/Principal Engineer         |
| data     | beginner     | Data Analyst                     |
| data     | intermediate | Data Scientist                   |
| data     | advanced     | Senior Data Scientist            |
| business | expert       | Director of Product / VP Product |

---

## Skill Priority Levels

### High Priority

- Core to role
- Blocking proficiency
- Must-have skills

### Medium Priority

- Important but not blocking
- Enhances effectiveness
- Nice-to-have fundamentals

### Low Priority

- Optional specializations
- Advanced topics
- Nice-to-have extras

---

## Testing

### Run All Tests

```bash
# Service integration tests
python test_integration.py

# End-to-end data flow
python test_data_flow.py

# Database verification
python test_database.py

# Flask startup check
python test_startup.py
```

### Test a Single Service

```python
# Test role engine
from services.roles import get_role_for_profile
result = get_role_for_profile("ai", "intermediate")
assert result["role"] == "AI Engineer"
print("✓ Role engine working")

# Test skill gaps
from services.skill_gap_advanced import get_skill_gap_advanced
gap = get_skill_gap_advanced("Software Engineer")
assert len(gap["core_skills"]) > 0
print("✓ Skill gaps working")

# Test readiness
from services.readiness_advanced import calculate_readiness_advanced
score = calculate_readiness_advanced("AI Engineer", ["Python"])
assert 0 <= score["readiness_score"] <= 100
print("✓ Readiness scoring working")
```

---

## Common Tasks

### Add a New Role

1. Edit `services/roles.py`
2. Add entry to `ROLE_ENGINE` dict:
   ```python
   "data": {
       "beginner": {"role": "Data Analyst", "next": "junior"},
       # ... etc
   }
   ```
3. Add skills to `services/skill_gap_advanced.py`
4. Test with `test_integration.py`

### Add a New Skill to a Role

1. Edit `services/skill_gap_advanced.py`
2. Find the role in `SKILL_REQUIREMENTS` dict
3. Add to `core_skills` or `optional_skills`:
   ```python
   {
       "name": "Skill Name",
       "priority": "High",
       "weight": 15,
       "reason": "Why it matters",
       "impact": "Effect of having it"
   }
   ```

### Change Experience Levels

1. Edit `services/roles.py` - Update `EXPERIENCE_LEVELS` constant
2. Edit `templates/index.html` - Update dropdown options
3. Edit any roles or skill requirements that reference old levels
4. Update documentation

### Create Admin Report

```python
from database.models import fetch_all_logs
import json

logs = fetch_all_logs()
by_role = {}

for log in logs:
    role = log['recommendation']
    if role not in by_role:
        by_role[role] = []
    by_role[role].append(log)

for role, submissions in by_role.items():
    avg_readiness = sum(s['readiness_score'] for s in submissions) / len(submissions)
    print(f"{role}: {len(submissions)} submissions, avg readiness {avg_readiness:.0f}%")
```

---

## Troubleshooting

### Error: "Invalid selection. Please choose a valid interest and level."

- Check that interest is one of: ai, tech, data, design, business
- Check that level is one of: beginner, junior, intermediate, advanced, expert
- Verify role exists in `ROLE_ENGINE` dict

### Error: "no such table: submissions"

- Run: `python -c "from database.models import create_table; create_table()"`
- Check database path in `config.py`

### Readiness score is 0%

- Check that `acquired_skills` list is not empty
- Verify skills match (case-insensitive substring matching)
- Check role exists in `SKILL_REQUIREMENTS` dict

### Database migration failed

- Check SQLite has ALTER TABLE support (SQLite 3.25.0+)
- Try: `python test_database.py` to diagnose
- Backup database and try manual schema update

---

## Performance Notes

- Role engine: O(1) lookup - 25 roles cached in memory
- Skill gaps: O(n) where n = number of skills per role (4-8)
- Readiness: O(m\*n) where m = acquired skills, n = required skills (fast for <100 skills)
- Database: Indexed on ID, no query optimization needed for current scale

---

## Security Notes

- ✅ Parameterized queries (no SQL injection)
- ✅ Input validation on all form fields
- ✅ Admin credentials from environment variables
- ✅ Session security headers configured
- ⚠️ No rate limiting (add if needed for production)
- ⚠️ HTTPS recommended for production

---

## Future Enhancements

1. **User Accounts**
   - Save profiles for repeat analysis
   - Track progress over time
   - Personalized recommendations

2. **Advanced Analytics**
   - Skill demand analysis
   - Career path success rates
   - Time-to-proficiency estimates

3. **Learning Resources**
   - Link to courses for skills
   - Estimated learning time
   - Cost estimates

4. **AI-Powered Insights**
   - Predict which skills take longest to learn
   - Suggest optimal learning order
   - Industry trend analysis

5. **Admin Features**
   - Export analytics to CSV
   - Filter submissions by date range
   - Role distribution charts
   - Readiness heatmap by role
