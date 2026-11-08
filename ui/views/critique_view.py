"""
Critique View: Actionable ATS Optimizer, Score Boost Roadmap, and Drop-In Replacements.
"""

import streamlit as st

from core.llm import get_llm, resolve_model_name
from core.critique import generate_critique


def render_critique_view(config: dict):
    """Render the ATS Checker, Exact Action Roadmap, and Drop-in Replacement tab."""
    st.markdown("### 🎯 Step 3: ATS Score Optimizer & Exact Resume Fixes")
    st.markdown(
        "Audit your resume through the lens of modern Applicant Tracking Systems (ATS) and elite technical recruiters. "
        "Discover your current ATS score, see your **potential 90+ score**, and get **exact copy-pasteable replacement text** "
        "crafted using **Google's XYZ formula** (*Accomplished [X] as measured by [Y] by doing [Z]*)."
    )

    vector_store = st.session_state.get("vector_store")
    raw_text = st.session_state.get("raw_text")

    if vector_store is None and not raw_text:
        st.warning(
            "⚠️ **No resume currently loaded.** Please go to the **Upload & Index Resume** tab "
            "and upload a resume before running the ATS audit.",
            icon="⚠️",
        )
        return

    server_models = config.get("server_models", [])
    resolved_model = resolve_model_name(config["llm_model"], server_models)

    st.caption(f"🧠 Analysis will run using model: **`{resolved_model}`**")

    col1, col2 = st.columns([1, 3])
    with col1:
        generate_btn = st.button(
            "⚡ Run ATS Audit & Exact Fix Engine",
            type="primary",
            use_container_width=True,
            help="Perform deep ATS scan and generate step-by-step exact text replacements",
        )

    # Perform Generation
    if generate_btn:
        with st.spinner(f"Analyzing resume flaws and drafting exact 90+ score replacements with `{resolved_model}`..."):
            try:
                llm = get_llm(
                    model_name=resolved_model,
                    base_url=config["base_url"],
                    available_models=server_models,
                )
                critique_data, markdown_output = generate_critique(
                    llm,
                    vector_store=vector_store,
                    raw_text=raw_text,
                )
                st.session_state["critique_data"] = critique_data
                st.session_state["critique_markdown"] = markdown_output
                st.toast("ATS Action Plan & Exact Fixes Generated!", icon="🎉")
            except Exception as e:
                err_msg = str(e)
                if "not found" in err_msg.lower() or "404" in err_msg:
                    st.error(
                        f"⚠️ **Model Not Found in Ollama**: `{resolved_model}`\n\n"
                        f"**Details:** {err_msg}\n\n"
                        f"👉 **Quick Fix:** In the left sidebar, check **Installed Models** to see what is loaded, "
                        f"or run `ollama pull {resolved_model}` in your terminal."
                    )
                else:
                    st.error(f"Failed to generate critique: {e}")
                return

    # Render Display if critique exists in session
    critique_data = st.session_state.get("critique_data")
    critique_markdown = st.session_state.get("critique_markdown")

    if critique_data and critique_markdown:
        st.divider()

        score = critique_data.get("ats_score", 72)
        potential = critique_data.get("potential_score", 94)
        gain = max(0, potential - score)
        breakdown = critique_data.get("score_breakdown", {})
        roadmap = critique_data.get("score_boost_roadmap", [])
        replacements = critique_data.get("ready_to_paste_replacements", {})
        keywords = critique_data.get("keywords", {})
        blueprint = critique_data.get("top_class_blueprint", [])
        roles = critique_data.get("suggested_career_roles", [])

        # 1. Dual Score Progression Hero Banner
        score_color = "#ef4444" if score < 70 else ("#f59e0b" if score < 85 else "#10b981")

        st.markdown(
            f"""
            <div class="score-comparison-banner">
                <div class="score-col-box">
                    <div class="score-col-label">Current ATS Score</div>
                    <div class="score-big-number" style="color: {score_color};">{score}<span style="font-size: 1.5rem; color: #94a3b8;">/100</span></div>
                    <span class="badge {'badge-red' if score < 70 else ('badge-amber' if score < 85 else 'badge-green')}">
                        {'Needs Major Fixes' if score < 70 else ('Competitive with Gaps' if score < 85 else 'FAANG Ready')}
                    </span>
                </div>
                <div class="score-arrow">➔</div>
                <div class="score-col-box">
                    <div class="score-col-label">Potential Score After Fixes</div>
                    <div class="score-big-number" style="color: #34d399;">{potential}<span style="font-size: 1.5rem; color: #94a3b8;">/100</span></div>
                    <div class="score-gain-badge">🚀 +{gain} PTS GAIN POSSIBLE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Sub-Score Metrics
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric(
                "📐 Format & Structure",
                f"{breakdown.get('format_structure', 75)}/100",
                help="Standard headings, single-column layout, contact data completeness",
            )
        with sc2:
            st.metric(
                "📊 Metric Impact (XYZ)",
                f"{breakdown.get('quantifiable_impact', 65)}/100",
                help="Proportion of bullets containing numbers, percentages, or dollar scale",
            )
        with sc3:
            st.metric(
                "⚡ Action Verb Power",
                f"{breakdown.get('action_verbs', 70)}/100",
                help="Active leadership verbs vs passive phrases like 'responsible for'",
            )
        with sc4:
            st.metric(
                "🔑 Keyword Density",
                f"{breakdown.get('keyword_richness', 75)}/100",
                help="Matching high-volume recruiter Boolean search terms",
            )

        if roles:
            roles_html = " ".join(f'<span class="badge badge-purple">{r}</span>' for r in roles)
            st.markdown(f"**🎯 Target Role Alignments:** {roles_html}", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Interactive Deep-Dive Tabs
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs(
            [
                "🚀 Exact Changes (Roadmap to 90+)",
                "📋 Drop-In Ready Sections",
                "🔑 Keyword Optimizer",
                "🏆 Top 1% Blueprint",
                "📊 Where You Lost Points",
            ]
        )

        # TAB 1: EXACT STEP-BY-STEP CHANGES (Direct answer to user prompt!)
        with sub_tab1:
            st.markdown(f"#### 🚀 Step-by-Step Action Plan to Reach {potential}+ Score")
            st.markdown(
                f"Implementing the **{len(roadmap)} prioritized changes** below will close your ATS gaps "
                f"and boost your score by **+{gain} points**. For every change, we've identified the exact text to replace."
            )

            for item in roadmap:
                step_num = item.get("step", 1)
                title = item.get("title", "")
                boost = item.get("score_boost", "+5 pts")
                priority = item.get("priority", "HIGH")
                section = item.get("section", "Experience")
                remove_txt = item.get("exact_text_to_remove", "")
                add_txt = item.get("exact_text_to_add", "")
                why = item.get("why_this_boosts_score", "")

                priority_badge = (
                    "badge-red" if priority == "CRITICAL" else ("badge-amber" if priority == "HIGH" else "badge-blue")
                )

                st.markdown(
                    f"""
                    <div class="action-step-card">
                        <div class="action-step-header">
                            <span class="action-step-title">Step {step_num}: {title}</span>
                            <div>
                                <span class="badge {priority_badge}">{priority}</span>
                                <span class="badge badge-green" style="font-weight: 800;">{boost} BOOST</span>
                            </div>
                        </div>
                        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 8px;">
                            📍 <strong>Where in your resume:</strong> <code>{section}</code>
                        </div>
                        <div style="font-size: 0.95rem; color: #334155; margin-bottom: 12px;">
                            💡 <strong>Why this boosts your score:</strong> {why}
                        </div>
                        <div class="before-box">
                            <strong>❌ REMOVE THIS FROM YOUR RESUME:</strong><br>
                            "{remove_txt}"
                        </div>
                        <div class="after-box">
                            <strong>✅ PASTE THIS EXACT REPLACEMENT INSTEAD:</strong><br>
                            "{add_txt}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Copy button helper for the replacement text
                with st.expander(f"📋 Click to Copy Replacement Text for Step {step_num}", expanded=False):
                    st.code(add_txt, language="text")

        # TAB 2: DROP-IN READY SECTIONS
        with sub_tab2:
            st.markdown("#### 📋 Drop-In Ready Sections (Copy & Paste)")
            st.markdown(
                "Here are your completely rewritten, ATS-optimized sections ready to be pasted directly into your document editor."
            )

            # 1. Summary
            st.markdown("##### 1️⃣ Optimized Professional Summary")
            st.caption("Replaces generic fluff with your actual degree, technical specializations, and quantifiable value.")
            summary_text = replacements.get("optimized_summary", "")
            if summary_text:
                st.code(summary_text, language="text")
            else:
                st.info("No summary replacement provided.")

            st.divider()

            # 2. Bullets
            st.markdown("##### 2️⃣ Quantified Experience & Project Bullets (Google XYZ Formula)")
            st.caption("Formula: **Accomplished [X] as measured by [Y] by doing [Z]**")
            opt_bullets = replacements.get("optimized_experience_bullets", [])
            if opt_bullets:
                for idx, b in enumerate(opt_bullets, 1):
                    role_name = b.get("role_or_project", f"Experience / Project {idx}")
                    orig = b.get("original_bullet", "")
                    opt = b.get("optimized_bullet", "")

                    st.markdown(f"**📌 {role_name}**")
                    st.markdown(
                        f"""
                        <div class="before-box" style="margin-bottom: 6px;">
                            <strong>❌ Current Text:</strong> "{orig}"
                        </div>
                        <div class="after-box" style="margin-bottom: 10px;">
                            <strong>✅ High-Impact XYZ Version:</strong> "{opt}"
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.code(opt, language="text")
            else:
                st.info("Current bullet points already display strong quantifiable metrics.")

            st.divider()

            # 3. Skills Block
            st.markdown("##### 3️⃣ Categorized Technical Skills Block (ATS-Compliant)")
            st.caption("Clean, single-column categorization with high-priority industry keywords already woven in.")
            skills_block = replacements.get("optimized_skills_block", "")
            if skills_block:
                st.code(skills_block, language="text")

            st.divider()

            # 4. Words to delete
            st.markdown("##### 4️⃣ Red-Flag Words to Delete Immediately")
            st.caption("These vague filler phrases dilute impact and are penalized by ATS scoring models.")
            red_flags = replacements.get("red_flag_words_to_delete", [])
            if red_flags:
                for rf in red_flags:
                    found = rf.get("found_phrase", "")
                    rep = rf.get("replace_with", "")
                    st.markdown(f"- ❌ Delete: **`{found}`** $\\longrightarrow$ ✅ Replace with: **`{rep}`**")
            else:
                st.success("No critical buzzwords detected.")

        # TAB 3: KEYWORDS
        with sub_tab3:
            st.markdown("#### 🔑 Keyword & Skills Analysis")
            st.markdown(
                "ATS engines screen for exact technical keywords. Ensure your resume contains both hard tools and strong verbs."
            )

            # Detected Skills
            detected = keywords.get("detected_skills", [])
            st.markdown("##### ✅ Hard Skills Detected in Resume")
            if detected:
                pills_html = " ".join(f'<span class="keyword-pill keyword-pill-green">✓ {s}</span>' for s in detected)
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.caption("No specific domain tools detected.")

            st.divider()

            # Missing Keywords
            missing = keywords.get("missing_high_priority_keywords", [])
            st.markdown("##### ⚠️ Missing In-Demand Keywords (Add These to Skills Section)")
            st.caption("These high-volume keywords are searched by recruiters for these job roles.")
            if missing:
                missing_html = " ".join(f'<span class="keyword-pill keyword-pill-amber">+ {m}</span>' for m in missing)
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.success("Great job! No major keyword gaps detected.")

            st.divider()

            # Action Verbs
            verbs = keywords.get("recommended_action_verbs", [])
            st.markdown("##### ⚡ High-Impact Power Action Verbs")
            if verbs:
                verbs_html = " ".join(f'<span class="keyword-pill keyword-pill-blue">⚡ {v}</span>' for v in verbs)
                st.markdown(verbs_html, unsafe_allow_html=True)

        # TAB 4: TOP 1% BLUEPRINT
        with sub_tab4:
            st.markdown("#### 🏆 Blueprint of a Top 1% Class Resume")
            st.markdown(
                "Follow these standard rules to ensure your resume consistently ranks in the top tier of major ATS software:"
            )

            if blueprint:
                for i, rule in enumerate(blueprint, 1):
                    st.markdown(f"**{i}.** {rule}")

            st.markdown(
                """
                ---
                ##### 📐 Golden Rules of ATS Formatting
                - **Single-Column Layout**: Never use two-column templates or tables; ATS parsers read left-to-right across columns, corrupting experience dates.
                - **Quantify Everything**: Target measurable numbers (%, $, time saved, users reached) in at least 60% of your experience bullet points.
                - **Standard Section Headings**: Use plain headers (`Professional Summary`, `Work Experience`, `Technical Skills`, `Education`).
                - **Standard Dates**: Format as `MM/YYYY – MM/YYYY` or `Month YYYY – Present`.
                - **File Format**: Standard `.pdf` or `.docx` with zero graphics, icons, or text boxes.
                """
            )

        # TAB 5: ITEMIZED POINT-DEDUCTION BREAKDOWN
        with sub_tab5:
            st.markdown("#### 📊 Itemized Point-Deduction Breakdown")
            st.markdown(
                f"Your resume scored **{score}/100**. Here's exactly where the **{100 - score} lost points** went, "
                f"broken down across 4 scoring categories (each worth 25 points)."
            )

            deductions_list = critique_data.get("point_deductions", [])
            grand_awarded = 0
            grand_lost = 0

            cat_icons = {
                "Format & Structure": "📐",
                "Quantifiable Impact": "📊",
                "Action Verbs & Tone": "⚡",
                "Keyword Richness & ATS Match": "🔑",
            }

            for cat_entry in deductions_list:
                cat_name = cat_entry.get("category", "Unknown")
                max_pts = cat_entry.get("max_points", 25)
                awarded = cat_entry.get("points_awarded", 25)
                lost = cat_entry.get("points_lost", 0)
                grand_awarded += awarded
                grand_lost += lost
                deds = cat_entry.get("deductions", [])
                pct = int(awarded / max_pts * 100) if max_pts > 0 else 0
                icon = cat_icons.get(cat_name, "📋")

                # Color based on percentage
                if pct >= 85:
                    bar_color = "#10b981"
                    status_cls = "badge-green"
                elif pct >= 60:
                    bar_color = "#f59e0b"
                    status_cls = "badge-amber"
                else:
                    bar_color = "#ef4444"
                    status_cls = "badge-red"

                # Category card with progress bar
                st.markdown(
                    f"""
                    <div class="deduction-category-card">
                        <div class="deduction-cat-header">
                            <span class="deduction-cat-title">{icon} {cat_name}</span>
                            <span class="badge {status_cls}" style="font-size: 0.85rem;">{awarded}/{max_pts} pts</span>
                        </div>
                        <div class="deduction-progress-track">
                            <div class="deduction-progress-fill" style="width: {pct}%; background: {bar_color};"></div>
                        </div>
                        <div class="deduction-progress-labels">
                            <span>0</span>
                            <span style="color: {bar_color}; font-weight: 700;">{awarded} earned</span>
                            <span>{max_pts}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if deds:
                    with st.expander(f"🔍 {len(deds)} deduction{'s' if len(deds) != 1 else ''} totaling -{lost} points — click to see details", expanded=True):
                        for d in deds:
                            d_issue = d.get("issue", "Unknown issue")
                            d_lost = d.get("points_lost", 0)
                            d_fix = d.get("fix", "No fix provided")
                            st.markdown(
                                f"""
                                <div class="deduction-row">
                                    <div class="deduction-row-header">
                                        <span class="deduction-issue">❌ {d_issue}</span>
                                        <span class="deduction-pts-badge">-{d_lost} pts</span>
                                    </div>
                                    <div class="deduction-fix">
                                        💡 <strong>Fix:</strong> {d_fix}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.success(f"✅ Full marks! No deductions in {cat_name}.")

                st.markdown("<br>", unsafe_allow_html=True)

            # Summary ledger table
            potential_after = min(100, grand_awarded + grand_lost)
            st.markdown("---")
            st.markdown(
                f"""
                <div class="deduction-summary-table">
                    <div class="deduction-summary-row">
                        <span class="deduction-summary-label">✅ Total Points Earned</span>
                        <span class="deduction-summary-value" style="color: #10b981;">{grand_awarded} / 100</span>
                    </div>
                    <div class="deduction-summary-row">
                        <span class="deduction-summary-label">❌ Total Points Lost</span>
                        <span class="deduction-summary-value" style="color: #ef4444;">-{grand_lost}</span>
                    </div>
                    <div class="deduction-summary-row" style="border-top: 2px solid #e2e8f0; padding-top: 12px; margin-top: 8px;">
                        <span class="deduction-summary-label">🎯 Current ATS Score</span>
                        <span class="deduction-summary-value" style="font-size: 1.5rem; color: #0f172a;">{score} / 100</span>
                    </div>
                    <div class="deduction-summary-row">
                        <span class="deduction-summary-label">🚀 Potential After All Fixes</span>
                        <span class="deduction-summary-value" style="font-size: 1.5rem; color: #10b981;">{potential} / 100</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Download Report Option
        st.download_button(
            label="📥 Download Full ATS Action Plan (.md)",
            data=critique_markdown,
            file_name=f"ATS_Score_Boost_Plan_{st.session_state.get('indexed_doc_name', 'candidate')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    elif not generate_btn:
        st.info("Click **⚡ Run ATS Audit & Exact Fix Engine** above to generate your score roadmap and exact replacements.")
