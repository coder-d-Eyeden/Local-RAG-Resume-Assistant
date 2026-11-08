"""
Structured ATS Checker and Resume Optimization module.
Evaluates resume against Applicant Tracking System (ATS) criteria, identifies specific flaws,
calculates potential score gain, and provides exact, copy-pasteable replacement text.
"""

import json
import re
from typing import Dict, Any, Tuple, Optional

from langchain_core.prompts import ChatPromptTemplate


CRITIQUE_PROMPT_TEMPLATE = """
You are a Principal Technical Recruiter and Senior ATS Optimization Specialist for top-tier tech companies (FAANG, Fortune 500, unicorns).

Your job is NOT just to give a score or generic feedback. The candidate needs to know EXACTLY what is lowering their score, how many points each change is worth, and the EXACT text to replace in their resume to reach a 90+ score.

Analyze the provided resume context thoroughly and output a VALID JSON object adhering strictly to the schema below.

CRITICAL INSTRUCTIONS:
1. Provide an honest current "ats_score" (0-100) and a realistic "potential_score" (typically 90-98) achieved after applying your exact fixes.
2. In "score_boost_roadmap", provide 4 prioritized, concrete steps. For EVERY step:
   - State the exact section in the resume.
   - Quote the EXACT weak or unoptimized text currently in their resume in "exact_text_to_remove".
   - Write the EXACT high-impact, ATS-optimized replacement text in "exact_text_to_add".
   - Provide the specific score boost (e.g. "+8 pts", "+6 pts").
3. In "ready_to_paste_replacements":
   - "optimized_summary": Write a complete, elite 3-4 sentence professional summary tailored to this candidate's actual background, with zero fluff and maximum keyword density.
   - "optimized_experience_bullets": Provide at least 2-3 specific bullet rewrites using Google's XYZ formula: "Accomplished [X] as measured by [Y] by doing [Z]" with concrete numbers, percentages, or scale.
   - "optimized_skills_block": Provide a perfectly formatted, ATS-compliant skills section grouped cleanly by category (e.g. Languages, Machine Learning & AI, Analytics & BI, Databases, Developer Tools & Platforms).
   - "red_flag_words_to_delete": Identify specific weak words or buzzwords found in the resume (e.g., "responsible for", "collaborated with", "hands-on experience", "strong communication skills") and their strong replacements.
4. In "keywords", extract hard skills found, missing high-priority keywords that recruiters in this domain search for, and recommended power action verbs.

Respond ONLY with a VALID JSON object in this exact schema with NO extraneous text:

{{
    "ats_score": 72,
    "potential_score": 94,
    "score_boost_roadmap": [
        {{
            "step": 1,
            "title": "Rewrite Professional Summary with Quantified Specialization",
            "score_boost": "+8 pts",
            "priority": "CRITICAL",
            "section": "Professional Summary",
            "exact_text_to_remove": "Quote exact weak text from candidate's summary",
            "exact_text_to_add": "Exact drop-in replacement paragraph with metrics and specialization",
            "why_this_boosts_score": "Explains how this fixes ATS keyword indexing and recruiter drop-off"
        }},
        {{
            "step": 2,
            "title": "Convert Passive Task Bullets to Google XYZ Quantified Achievements",
            "score_boost": "+7 pts",
            "priority": "CRITICAL",
            "section": "Work Experience / Key Projects",
            "exact_text_to_remove": "Quote exact weak bullet from resume",
            "exact_text_to_add": "Exact rewritten bullet with numbers, percentages, and scale",
            "why_this_boosts_score": "Replaces generic task statements with measurable business impact"
        }},
        {{
            "step": 3,
            "title": "Restructure Skills Section to Include Missing In-Demand Keywords",
            "score_boost": "+5 pts",
            "priority": "HIGH",
            "section": "Technical Skills",
            "exact_text_to_remove": "Current unorganized or incomplete skills text",
            "exact_text_to_add": "Pristine categorized skills block ready to copy-paste",
            "why_this_boosts_score": "Matches search queries recruiters execute in Greenhouse/Workday"
        }},
        {{
            "step": 4,
            "title": "Purge Vague Fluff and Passive Buzzwords",
            "score_boost": "+3 pts",
            "priority": "MEDIUM",
            "section": "Throughout Resume",
            "exact_text_to_remove": "Specific passive phrases present in their resume",
            "exact_text_to_add": "Power action verb replacements",
            "why_this_boosts_score": "Eliminates clichés that reduce hiring manager interest"
        }}
    ],
    "ready_to_paste_replacements": {{
        "optimized_summary": "Full polished 3-4 sentence summary ready to copy-paste directly into resume",
        "optimized_experience_bullets": [
            {{
                "role_or_project": "Role or project name from candidate's resume",
                "original_bullet": "Original text from resume",
                "optimized_bullet": "Rewritten bullet using Google XYZ formula (Accomplished [X] measured by [Y] by doing [Z])"
            }},
            {{
                "role_or_project": "Second role or project from candidate's resume",
                "original_bullet": "Original text from resume",
                "optimized_bullet": "Rewritten bullet with metrics"
            }}
        ],
        "optimized_skills_block": "Languages: ... | Data Science & ML: ... | Databases: ... | Tools: ...",
        "red_flag_words_to_delete": [
            {{
                "found_phrase": "Weak phrase found in their resume",
                "replace_with": "Strong active verb or concise metric"
            }}
        ]
    }},
    "score_breakdown": {{
        "format_structure": 75,
        "quantifiable_impact": 60,
        "action_verbs": 70,
        "keyword_richness": 75
    }},
    "point_deductions": [
        {{
            "category": "Format & Structure",
            "max_points": 25,
            "points_awarded": 19,
            "points_lost": 6,
            "deductions": [
                {{"issue": "Missing professional summary section", "points_lost": 3, "fix": "Add a 3-sentence summary with role title, years of experience, and top 3 technical skills"}},
                {{"issue": "Inconsistent date formatting", "points_lost": 2, "fix": "Standardize all dates to MM/YYYY – MM/YYYY or Month YYYY – Present format"}},
                {{"issue": "Non-standard section headings", "points_lost": 1, "fix": "Use standard headings: Professional Summary, Work Experience, Technical Skills, Education"}}
            ]
        }},
        {{
            "category": "Quantifiable Impact",
            "max_points": 25,
            "points_awarded": 15,
            "points_lost": 10,
            "deductions": [
                {{"issue": "Experience bullets lack measurable metrics", "points_lost": 6, "fix": "Rewrite bullets using Google XYZ formula: Accomplished [X] as measured by [Y] by doing [Z]"}},
                {{"issue": "No revenue, scale, or performance numbers anywhere", "points_lost": 4, "fix": "Add specific numbers: users served, percentage improvements, records processed, time saved"}}
            ]
        }},
        {{
            "category": "Action Verbs & Tone",
            "max_points": 25,
            "points_awarded": 18,
            "points_lost": 7,
            "deductions": [
                {{"issue": "Uses passive phrases like 'responsible for' or 'worked on'", "points_lost": 4, "fix": "Replace every 'responsible for' with power verbs: Spearheaded, Engineered, Orchestrated, Automated"}},
                {{"issue": "Weak opening verbs on multiple bullet points", "points_lost": 3, "fix": "Start every bullet with a strong past-tense action verb (Accelerated, Architected, Deployed, Optimized)"}}
            ]
        }},
        {{
            "category": "Keyword Richness & ATS Match",
            "max_points": 25,
            "points_awarded": 20,
            "points_lost": 5,
            "deductions": [
                {{"issue": "Missing critical industry keywords recruiters search for", "points_lost": 3, "fix": "Add missing keywords to Technical Skills: Docker, CI/CD, AWS/GCP, Model Deployment, MLOps"}},
                {{"issue": "Skills section not categorized for ATS parsing", "points_lost": 2, "fix": "Group skills by category: Languages | Frameworks | Cloud & DevOps | Databases | ML & Analytics"}}
            ]
        }}
    ],
    "keywords": {{
        "detected_skills": ["Skill 1", "Skill 2"],
        "missing_high_priority_keywords": ["Missing Tool 1", "Missing Methodology 2"],
        "recommended_action_verbs": ["Spearheaded", "Architected", "Orchestrated", "Accelerated", "Automated"]
    }},
    "top_class_blueprint": [
        "Enforce Google's XYZ formula on 100% of experience bullet points.",
        "Maintain clean single-column format with standard headings (Summary, Experience, Skills, Education).",
        "Target 40-50% keyword density match against specific job descriptions."
    ],
    "suggested_career_roles": ["Primary Role", "Secondary Role", "Senior/Emerging Role"]
}}

--- CANDIDATE RESUME CONTEXT ---
{context}
--- END CANDIDATE RESUME CONTEXT ---
"""


def extract_full_resume_context(vector_store) -> str:
    """Retrieve and combine all chunks from the vector store."""
    if vector_store is None:
        return ""
    try:
        data = vector_store.get()
        documents = data.get("documents", [])
        return "\n\n---\n\n".join(documents)
    except Exception as e:
        print(f"Error extracting context from vector store: {e}")
        return ""


def _sanitize_score(val: Any, default: int = 70) -> int:
    """Ensure score is an integer between 0 and 100."""
    try:
        if isinstance(val, (int, float)):
            return max(0, min(100, int(val)))
        if isinstance(val, str):
            match = re.search(r"\d+", val)
            if match:
                return max(0, min(100, int(match.group())))
    except Exception:
        pass
    return default


def parse_critique_json(response_text: str) -> Dict[str, Any]:
    """Parse JSON response from the LLM with robust extraction and normalization."""
    response_text = response_text.strip()
    data = None

    # 1. Direct JSON parse
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # 2. Extract JSON block between markdown code fences
    if data is None:
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if fence_match:
            try:
                data = json.loads(fence_match.group(1))
            except json.JSONDecodeError:
                pass

    # 3. Match from outermost { to }
    if data is None:
        brace_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
        if brace_match:
            try:
                data = json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass

    # 4. Fallback default structure if parsing completely fails
    if not isinstance(data, dict):
        data = {
            "ats_score": 70,
            "potential_score": 92,
            "score_boost_roadmap": [
                {
                    "step": 1,
                    "title": "Rewrite Professional Summary with Quantified Value Proposition",
                    "score_boost": "+8 pts",
                    "priority": "CRITICAL",
                    "section": "Professional Summary",
                    "exact_text_to_remove": "Generic summary statement",
                    "exact_text_to_add": "Results-driven specialist with hands-on expertise delivering end-to-end solutions.",
                    "why_this_boosts_score": "Grabs recruiter attention in the first 6 seconds and matches ATS title indexing.",
                },
                {
                    "step": 2,
                    "title": "Add Measurable Metrics to Experience Bullets (Google XYZ Formula)",
                    "score_boost": "+7 pts",
                    "priority": "CRITICAL",
                    "section": "Work Experience",
                    "exact_text_to_remove": "Task-oriented passive bullet point",
                    "exact_text_to_add": "Engineered automated data pipelines, accelerating processing speed by 35% across 50K+ records.",
                    "why_this_boosts_score": "Recruiters and ATS score quantified bullets 3x higher than passive task descriptions.",
                },
                {
                    "step": 3,
                    "title": "Incorporate High-Priority Missing Keywords",
                    "score_boost": "+5 pts",
                    "priority": "HIGH",
                    "section": "Technical Skills",
                    "exact_text_to_remove": "Uncategorized skills list",
                    "exact_text_to_add": "Languages: Python, SQL | Frameworks: PyTorch, Scikit-learn | Tools: Docker, Git, CI/CD",
                    "why_this_boosts_score": "Matches high-volume Boolean search queries used by hiring managers.",
                },
                {
                    "step": 4,
                    "title": "Remove Vague Buzzwords and Clichés",
                    "score_boost": "+3 pts",
                    "priority": "MEDIUM",
                    "section": "Throughout Resume",
                    "exact_text_to_remove": "Phrases like 'team player', 'responsible for', 'strong communication'",
                    "exact_text_to_add": "Action verbs: 'Spearheaded', 'Orchestrated', 'Optimized'",
                    "why_this_boosts_score": "Eliminates empty fluff that weakens professional credibility.",
                },
            ],
            "ready_to_paste_replacements": {
                "optimized_summary": "Data & Software Professional with expertise in end-to-end system design, automated data pipelines, and machine learning models.",
                "optimized_experience_bullets": [
                    {
                        "role_or_project": "Core Project",
                        "original_bullet": "Collaborated on an AI-driven project.",
                        "optimized_bullet": "Co-engineered an end-to-end predictive machine learning model, improving inference speed by 35%.",
                    }
                ],
                "optimized_skills_block": "Languages: Python, SQL | ML & Analytics: Scikit-learn, Regression, Forecasting | Tools: Git, Docker",
                "red_flag_words_to_delete": [
                    {"found_phrase": "responsible for", "replace_with": "Engineered / Spearheaded"},
                    {"found_phrase": "collaborated in a three-member team", "replace_with": "Co-engineered across a 3-member agile team"},
                ],
            },
            "score_breakdown": {
                "format_structure": 75,
                "quantifiable_impact": 65,
                "action_verbs": 70,
                "keyword_richness": 70,
            },
            "keywords": {
                "detected_skills": ["Python", "SQL", "Machine Learning"],
                "missing_high_priority_keywords": ["Docker", "Git", "CI/CD", "AWS/GCP", "Model Deployment"],
                "recommended_action_verbs": ["Spearheaded", "Architected", "Orchestrated", "Accelerated", "Automated"],
            },
            "top_class_blueprint": [
                "Quantify every achievement using Google's XYZ formula.",
                "Maintain clean single-column format for seamless ATS parsing.",
                "Incorporate exact role-specific keywords into your Technical Skills block.",
            ],
            "suggested_career_roles": ["Data Scientist", "Machine Learning Engineer", "BI Analyst"],
            "raw_response": response_text,
        }

    # Normalize scores
    data["ats_score"] = _sanitize_score(data.get("ats_score", 72))
    potential_raw = data.get("potential_score")
    if potential_raw:
        data["potential_score"] = _sanitize_score(potential_raw, default=min(96, data["ats_score"] + 20))
    else:
        data["potential_score"] = min(96, data["ats_score"] + 20)

    # Ensure potential_score is always higher than ats_score
    if data["potential_score"] <= data["ats_score"]:
        data["potential_score"] = min(98, data["ats_score"] + 18)

    # Normalize score breakdown
    sb = data.get("score_breakdown", {})
    if isinstance(sb, dict):
        data["score_breakdown"] = {
            "format_structure": _sanitize_score(sb.get("format_structure", 75)),
            "quantifiable_impact": _sanitize_score(sb.get("quantifiable_impact", 65)),
            "action_verbs": _sanitize_score(sb.get("action_verbs", 70)),
            "keyword_richness": _sanitize_score(sb.get("keyword_richness", 75)),
        }
    else:
        data["score_breakdown"] = {
            "format_structure": 75,
            "quantifiable_impact": 65,
            "action_verbs": 70,
            "keyword_richness": 75,
        }

    # Ensure score_boost_roadmap is a populated list
    if "score_boost_roadmap" not in data or not isinstance(data["score_boost_roadmap"], list) or len(data["score_boost_roadmap"]) == 0:
        data["score_boost_roadmap"] = [
            {
                "step": 1,
                "title": "Rewrite Professional Summary with Quantified Specialization",
                "score_boost": "+8 pts",
                "priority": "CRITICAL",
                "section": "Professional Summary",
                "exact_text_to_remove": "Generic summary statements lacking metrics",
                "exact_text_to_add": data.get("ready_to_paste_replacements", {}).get("optimized_summary", "High-impact summary with core tools and achievements."),
                "why_this_boosts_score": "Increases ATS role-matching accuracy and prevents hiring manager drop-off.",
            },
            {
                "step": 2,
                "title": "Adopt Google's XYZ Formula for Work Experience Bullets",
                "score_boost": "+7 pts",
                "priority": "CRITICAL",
                "section": "Work Experience / Projects",
                "exact_text_to_remove": "Passive task bullet points lacking measurable outcomes",
                "exact_text_to_add": "Rewritten XYZ bullet points featuring measurable metrics (%, numbers, scale).",
                "why_this_boosts_score": "Quantifiable achievements are heavily weighted by ATS scoring algorithms.",
            },
            {
                "step": 3,
                "title": "Inject Critical Missing Keywords into Skills Section",
                "score_boost": "+5 pts",
                "priority": "HIGH",
                "section": "Technical Skills",
                "exact_text_to_remove": "Current unorganized skills block",
                "exact_text_to_add": data.get("ready_to_paste_replacements", {}).get("optimized_skills_block", "Categorized technical skills matching industry standards."),
                "why_this_boosts_score": "Matches search queries recruiters execute in Applicant Tracking Systems.",
            },
            {
                "step": 4,
                "title": "Purge Vague Fluff and Buzzwords",
                "score_boost": "+3 pts",
                "priority": "MEDIUM",
                "section": "Throughout Resume",
                "exact_text_to_remove": "Empty clichés ('team player', 'responsible for', 'strong analytical skills')",
                "exact_text_to_add": "Power action verbs: 'Spearheaded', 'Orchestrated', 'Automated'",
                "why_this_boosts_score": "Elevates professional tone and aligns with senior-level resume standards.",
            },
        ]

    # Ensure ready_to_paste_replacements is populated
    if "ready_to_paste_replacements" not in data or not isinstance(data["ready_to_paste_replacements"], dict):
        data["ready_to_paste_replacements"] = {
            "optimized_summary": "Experienced professional with deep expertise in technical problem solving, data workflows, and scalable project delivery.",
            "optimized_experience_bullets": [],
            "optimized_skills_block": "Languages: Python, SQL | Frameworks: Scikit-learn, Pandas | Tools: Git, Docker",
            "red_flag_words_to_delete": [],
        }

    # Ensure keywords structure
    if "keywords" not in data or not isinstance(data["keywords"], dict):
        data["keywords"] = {"detected_skills": [], "missing_high_priority_keywords": [], "recommended_action_verbs": []}

    # Ensure blueprint & career roles
    if "top_class_blueprint" not in data or not isinstance(data["top_class_blueprint"], list):
        data["top_class_blueprint"] = []
    if "suggested_career_roles" not in data or not isinstance(data["suggested_career_roles"], list):
        data["suggested_career_roles"] = []

    # Normalize point_deductions: build from score_breakdown if LLM didn't provide it
    pd_raw = data.get("point_deductions")
    if not isinstance(pd_raw, list) or len(pd_raw) == 0:
        sb = data["score_breakdown"]
        category_map = [
            ("Format & Structure", "format_structure"),
            ("Quantifiable Impact", "quantifiable_impact"),
            ("Action Verbs & Tone", "action_verbs"),
            ("Keyword Richness & ATS Match", "keyword_richness"),
        ]
        generated = []
        for cat_name, sb_key in category_map:
            raw_score = sb.get(sb_key, 75)  # out of 100
            awarded = max(0, min(25, round(raw_score * 25 / 100)))
            lost = 25 - awarded
            deductions = []
            if lost > 0:
                deductions.append({
                    "issue": f"{cat_name} needs improvement",
                    "points_lost": lost,
                    "fix": f"Review and optimize the {cat_name.lower()} aspects of your resume",
                })
            generated.append({
                "category": cat_name,
                "max_points": 25,
                "points_awarded": awarded,
                "points_lost": lost,
                "deductions": deductions,
            })
        data["point_deductions"] = generated
    else:
        # Validate and normalize each category entry the LLM returned
        normalized = []
        for entry in pd_raw:
            if not isinstance(entry, dict):
                continue
            cat = entry.get("category", "Unknown Category")
            max_pts = int(entry.get("max_points", 25))
            awarded = int(entry.get("points_awarded", max_pts))
            lost = int(entry.get("points_lost", max_pts - awarded))
            # Ensure awarded + lost == max_pts
            if awarded + lost != max_pts:
                lost = max_pts - awarded
            deductions = entry.get("deductions", [])
            if not isinstance(deductions, list):
                deductions = []
            # Ensure individual deduction points sum to total lost (adjust last if needed)
            ded_sum = sum(int(d.get("points_lost", 0)) for d in deductions if isinstance(d, dict))
            if deductions and ded_sum != lost and lost > 0:
                remainder = lost - sum(int(d.get("points_lost", 0)) for d in deductions[:-1] if isinstance(d, dict))
                if isinstance(deductions[-1], dict):
                    deductions[-1]["points_lost"] = max(0, remainder)
            normalized.append({
                "category": cat,
                "max_points": max_pts,
                "points_awarded": awarded,
                "points_lost": lost,
                "deductions": deductions,
            })
        data["point_deductions"] = normalized if normalized else data.get("point_deductions", [])

    return data


def format_critique_markdown(data: Dict[str, Any]) -> str:
    """Format structured ATS audit data into a comprehensive, actionable Markdown report."""
    score = data.get("ats_score", 72)
    potential = data.get("potential_score", 94)
    gain = potential - score
    breakdown = data.get("score_breakdown", {})
    roadmap = data.get("score_boost_roadmap", [])
    replacements = data.get("ready_to_paste_replacements", {})
    keywords = data.get("keywords", {})
    blueprint = data.get("top_class_blueprint", [])
    roles = data.get("suggested_career_roles", [])

    # Tier badge
    if score >= 85:
        tier_badge = "🟢 **Tier 1: Highly Competitive (Top 10% ATS Ready)**"
    elif score >= 70:
        tier_badge = "🟡 **Tier 2: Competitive with Key Polish Needed**"
    else:
        tier_badge = "🔴 **Tier 3: Low ATS Match (High Rejection Risk)**"

    # Roadmap formatting
    roadmap_md = ""
    for item in roadmap:
        step_num = item.get("step", 1)
        title = item.get("title", "")
        boost = item.get("score_boost", "+5 pts")
        priority = item.get("priority", "HIGH")
        section = item.get("section", "")
        remove_txt = item.get("exact_text_to_remove", "")
        add_txt = item.get("exact_text_to_add", "")
        why = item.get("why_this_boosts_score", "")

        priority_icon = "🔴" if priority == "CRITICAL" else ("🟡" if priority == "HIGH" else "🔵")

        roadmap_md += f"""
#### {priority_icon} Step {step_num}: {title} `[{boost} Boost]`
- **Section:** `{section}` | **Priority:** `{priority}`
- **Why this boosts your score:** {why}
- **❌ EXACT TEXT TO REMOVE / REPLACE:**  
  > *"{remove_txt}"*
- **✅ EXACT REPLACEMENT TEXT TO PASTE:**  
  > **"{add_txt}"**

---
"""

    # Ready to paste bullets formatting
    bullets_md = ""
    opt_bullets = replacements.get("optimized_experience_bullets", [])
    for b in opt_bullets:
        bullets_md += f"""
- **Role / Project:** `{b.get('role_or_project', 'Project')}`
  - **❌ Original:** *"{b.get('original_bullet', '')}"*
  - **✅ Optimized (XYZ Formula):** **"{b.get('optimized_bullet', '')}"**
"""

    # Red flags formatting
    red_flags = replacements.get("red_flag_words_to_delete", [])
    red_flags_md = ""
    if red_flags:
        red_flags_md = "| Phrase Found in Resume | High-Impact Replacement |\n|---|---|\n"
        for rf in red_flags:
            red_flags_md += f"| ❌ `{rf.get('found_phrase', '')}` | ✅ **{rf.get('replace_with', '')}** |\n"
    else:
        red_flags_md = "No major buzzword red flags identified."

    # Keywords formatting
    detected_md = ", ".join(f"`{k}`" for k in keywords.get("detected_skills", [])) or "None identified"
    missing_md = ", ".join(f"`{k}`" for k in keywords.get("missing_high_priority_keywords", [])) or "None identified"
    verbs_md = ", ".join(f"**{v}**" for v in keywords.get("recommended_action_verbs", [])) or "None identified"

    # Blueprint formatting
    blueprint_md = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(blueprint))
    roles_md = " • ".join(roles) if roles else "Data / Software Professional"

    # Build point deductions section
    deductions_list = data.get("point_deductions", [])
    deductions_md = ""
    total_awarded = 0
    total_lost = 0
    for cat_entry in deductions_list:
        cat_name = cat_entry.get("category", "Unknown")
        max_pts = cat_entry.get("max_points", 25)
        awarded = cat_entry.get("points_awarded", 25)
        lost = cat_entry.get("points_lost", 0)
        total_awarded += awarded
        total_lost += lost
        deds = cat_entry.get("deductions", [])

        deductions_md += f"\n### {cat_name}: **{awarded}/{max_pts}** points earned ({lost} points lost)\n\n"
        if deds:
            deductions_md += "| # | Issue Costing You Points | Points Lost | How to Fix It |\n"
            deductions_md += "|:---:|---|:---:|---|\n"
            for idx, d in enumerate(deds, 1):
                d_issue = d.get("issue", "")
                d_lost = d.get("points_lost", 0)
                d_fix = d.get("fix", "")
                deductions_md += f"| {idx} | {d_issue} | **-{d_lost}** | {d_fix} |\n"
            deductions_md += "\n"
        else:
            deductions_md += "> ✅ No deductions — full marks in this category!\n\n"

    deductions_md += f"\n---\n\n**Score Ledger:** {total_awarded} points earned + {total_lost} points lost = {total_awarded + total_lost}/100\n\n"

    report = f"""# 🎯 ATS Resume Audit & Exact Score-Boost Blueprint

### Current ATS Score: **{score} / 100** $\\longrightarrow$ Target Potential Score: **{potential} / 100** `(+{gain} pts potential)`
{tier_badge}

| Evaluation Dimension | Current Score | Standard Required |
|---|:---:|:---:|
| 📐 Format & Parseability | **{breakdown.get('format_structure', 0)}/100** | $\\ge 85$ |
| 📊 Quantifiable Impact (Google XYZ) | **{breakdown.get('quantifiable_impact', 0)}/100** | $\\ge 80$ |
| ⚡ Action Verb Strength | **{breakdown.get('action_verbs', 0)}/100** | $\\ge 80$ |
| 🔑 Keyword Density & Relevance | **{breakdown.get('keyword_richness', 0)}/100** | $\\ge 85$ |

**Target Career Pathways:** {roles_md}

---

## 📊 Itemized Point-Deduction Breakdown (Where Your {100 - score} Lost Points Went)

Every point is accounted for below. Your resume is scored on 4 categories, each worth 25 points (totaling 100).

{deductions_md}

---

## 🚀 Exact Action Plan to Reach 90+ Score (`+{gain} Points Total`)
Implement the following prioritized changes in your resume to instantly boost your ATS match and recruiter response rate:

{roadmap_md}

---

## 📋 Ready-to-Paste Drop-In Replacements

### 1. Optimized Professional Summary (Drop-In Replacement)
```text
{replacements.get('optimized_summary', 'Tailored professional summary.')}
```

### 2. High-Impact Work Experience Bullets (Google XYZ Formula)
{bullets_md if bullets_md.strip() else "Your current bullet points already feature strong quantifiable metrics."}

### 3. Categorized Technical Skills Block (ATS-Compliant)
```text
{replacements.get('optimized_skills_block', 'Languages: Python, SQL | Tools: Git, Docker')}
```

### 4. Red-Flag Phrases to Delete Immediately
{red_flags_md}

---

## 🔑 Keyword & Skills Analysis

#### ✅ Detected Hard Skills Found in Resume
{detected_md}

#### ⚠️ High-Priority Missing Keywords (Add These to Pass ATS Filters)
{missing_md}

#### ⚡ Recommended Power Action Verbs
{verbs_md}

---

## 🏆 Blueprint of a Top 1% Class Resume
{blueprint_md}
"""
    return report


def generate_critique(
    llm,
    vector_store=None,
    raw_text: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """
    Generate structured ATS audit, score-boost roadmap, and exact replacement text.
    Accepts direct raw_text (preserves structure) or extracts from vector_store.
    
    Returns:
        (critique_data_dict, formatted_markdown_str)
    """
    context = raw_text or extract_full_resume_context(vector_store)
    if not context or not context.strip():
        raise ValueError("No resume content found. Please upload and index a resume first.")

    critique_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CRITIQUE_PROMPT_TEMPLATE),
            (
                "human",
                "Analyze the provided resume context thoroughly. Perform an executive ATS evaluation and return ONLY the valid JSON object specifying the exact text changes, score boost per step, and drop-in replacements.",
            ),
        ]
    )

    chain = critique_prompt | llm
    response = chain.invoke({"context": context})

    response_text = response if isinstance(response, str) else getattr(response, "content", str(response))
    critique_data = parse_critique_json(response_text)
    markdown_output = format_critique_markdown(critique_data)

    return critique_data, markdown_output
