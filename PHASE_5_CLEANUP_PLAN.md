# Phase 5: File Cleanup - Duplicate Service Removal

## Deletion Plan (12 Files)

### Files to Delete and Rationale

1. **roadmap.py** → Replaced by `roadmap_service.py`
   - Old static roadmap generation
   - Used by: `user_routes.py` (line 3)
   - Replacement ready: roadmap_service.py with dynamic generation
   - Status: SAFE TO DELETE

2. **readiness.py** → Can be replaced by career_engine logic
   - Old readiness scoring
   - Used by: `user_routes.py` (line 4, 81, 262)
   - Can integrate into career_engine.py or keep minimal implementation
   - Status: REVIEW NEEDED

3. **recommendations_engine.py** → Replaced by career_engine
   - Recommends roles based on skills
   - Uses skill_gap.py (also being deleted)
   - Used by: `user_routes.py` (line 5)
   - Replacement ready: career_engine.py
   - Status: SAFE TO DELETE

4. **action_plan.py** → Replaced by `action_guidance_service.py`
   - Old action plan generation
   - Used by: `user_routes.py` (line 6)
   - Replacement ready: action_guidance_service.py
   - Status: SAFE TO DELETE

5. **analysis.py** → Replaced by `analysis_pipeline.py`
   - Old analysis wrapper
   - Used by: `user_routes.py` (line 2)
   - Replacement ready: analysis_pipeline.py
   - Status: SAFE TO DELETE

6. **skill_gap.py** → Replaced by `skill_gap_analyzer.py`
   - Old skill gap assessment
   - Used by: `recommendations_engine.py` (line 8)
   - Replacement ready: skill_gap_analyzer.py
   - Status: SAFE TO DELETE

7. **resume_parser.py** → Replaced by `resume_parser_saas.py`
   - Old resume parsing
   - Used by: `career_ai_routes.py` (line 1151), `user_routes.py` (line 243), `resume_upload_service.py` (line 6)
   - Replacement ready: resume_parser_saas.py
   - Status: CHECK COMPATIBILITY FIRST

8. **resume_upload_service.py** → Integrated into routes
   - Old upload wrapper
   - Imports resume_parser.py
   - Functionality: Could be a route handler instead
   - Status: NEEDS REVIEW

9. **resume_evolution_planner.py** → Replaced by updated resume services
   - Old career planning
   - Used by: `guidance_routes.py` (line 10)
   - Replacement: Can use action_guidance_service + roadmap_service
   - Status: CHECK USAGE FIRST

10. **resume_detailed_analyzer.py** → Replaced by `resume_analysis_structured.py`
    - Duplicate resume analysis
    - Functionality: 3 resume analyzers exist (resume_analyzer.py, resume_detailed_analyzer.py, resume_analysis_structured.py)
    - Keep: resume_analyzer.py (primary), resume_analysis_structured.py (new)
    - Status: SAFE TO DELETE

11. **recommendation.py** → Replaced by career_engine
    - Old single recommendation
    - Duplicate of recommendations_engine.py
    - Status: SAFE TO DELETE

12. **chatbot_service.py** → Replaced by `ai_chatbot_service.py`
    - Old chatbot service
    - Duplicate: chatbot.py also exists
    - Keep: ai_chatbot_service.py (primary)
    - Status: SAFE TO DELETE

13. **chatbot.py** → Replaced by `ai_chatbot_service.py`
    - Old chatbot routes/logic
    - Not imported anywhere
    - Status: SAFE TO DELETE

---

## Import Update Plan

Before deletion, update these imports in:

### `user_routes.py` (Lines 2-6)

OLD:

```python
from services.analysis import analyze_profile
from services.roadmap import get_roadmap
from services.readiness import calculate_readiness
from services.recommendations_engine import get_detailed_recommendation
from services.action_plan import generate_action_plan
```

NEW:

```python
from services.analysis_pipeline import run_full_pipeline
from services.roadmap_service import generate_roadmap
from services.career_engine import calculate_career_confidence  # Replace readiness
from services.career_engine import get_detailed_recommendation  # From career_engine
from services.action_guidance_service import generate_action_guidance  # Replace action_plan
```

### `user_routes.py` (Lines 243, 262, 81)

OLD: `parse_resume_text` from services.resume_parser
NEW: `parse_resume_text` from services.resume_parser_saas

### `career_ai_routes.py` (Line 1151)

OLD: `parse_resume_text` from services.resume_parser
NEW: `parse_resume_text` from services.resume_parser_saas

### `guidance_routes.py` (Line 10)

OLD: `from services.resume_evolution_planner import ResumeEvolutionPlanner`
NEW: Remove import; use `roadmap_service` + `action_guidance_service` instead

### `recommendations_engine.py` (Line 8)

Will be deleted, so no update needed.

### `resume_upload_service.py` (Line 6)

Will be deleted, so no update needed.

---

## Execution Strategy

1. ✅ Update all imports to point to replacement services
2. ✅ Validate that no code breaks
3. ✅ Run syntax check on all modified files
4. ✅ Delete the 12 deprecated files
5. ✅ Final validation

---

## Expected Outcome

**Before:** 41 service files (with duplicates)
**After:** 29 service files (consolidated)
**Reduction:** -12 files (-29% reduction)

**Benefits:**

- Cleaner codebase
- No duplicate logic
- Easier to maintain
- Single source of truth for each capability

---

**Status:** Ready to execute
