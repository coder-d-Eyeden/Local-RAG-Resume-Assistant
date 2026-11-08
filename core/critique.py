"""
Structured Resume Critique module.
Uses LLM to evaluate the resume and output structured feedback.
"""

import json
import re
from typing import Dict, Any, Tuple

from langchain_core.prompts import ChatPromptTemplate


CRITIQUE_PROMPT_TEMPLATE = """
You are a world-class professional resume and career consultant.
Your task is to analyze the provided resume text below and provide a comprehensive assessment.

IMPORTANT: If the resume is already excellent and well-crafted, focus on highlighting its strengths and positive aspects rather than finding faults. Only suggest improvements if there are genuine areas that could be enhanced.

You MUST respond with a valid JSON object in exactly this format:
{{
    "overall_assessment": "Brief overall assessment of the resume quality (e.g., 'Excellent', 'Strong', 'Good with room for improvement', 'Needs significant work')",
    "summary_of_strengths": "A detailed summary of the resume's major strong points and what makes it effective.",
    "key_highlights": [
        "First standout feature or achievement",
        "Second impressive element",
        "Third notable strength"
    ],
    "key_areas_for_improvement": [
        "Only include if there are genuine areas for improvement. If resume is excellent, use 'No major improvements needed' or 'Minor suggestions only'"
    ],
    "suggested_career_path": "A suggestion for the most suitable career path or next job role based on the skills and experience provided.",
    "confidence_level": "Your confidence in this candidate's marketability (e.g., 'Very High', 'High', 'Moderate', 'Needs Development')"
}}

--- RESUME CONTEXT ---
{context}
--- END CONTEXT ---
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


def parse_critique_json(response_text: str) -> Dict[str, Any]:
    """Parse JSON response from the LLM with fallback regex extraction."""
    response_text = response_text.strip()
    
    # Try direct parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block between code fences
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try matching first { to last }
    brace_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback structure if JSON extraction completely failed
    return {
        "overall_assessment": "Analysis Completed",
        "summary_of_strengths": response_text,
        "key_highlights": ["See full response summary above."],
        "key_areas_for_improvement": ["No structured improvements parsed."],
        "suggested_career_path": "Refer to summary.",
        "confidence_level": "High",
        "raw_response": response_text,
    }


def format_critique_markdown(data: Dict[str, Any]) -> str:
    """Format structured critique data into a polished Markdown document."""
    overall = data.get("overall_assessment", "Evaluated")
    confidence = data.get("confidence_level", "Moderate")

    # Tone styling
    overall_lower = overall.lower()
    conf_lower = confidence.lower()
    if "excellent" in overall_lower or "very high" in conf_lower:
        emoji = "🏆"
        color = "#10b981"
    elif "strong" in overall_lower or "high" in conf_lower:
        emoji = "⭐"
        color = "#3b82f6"
    else:
        emoji = "📋"
        color = "#6b7280"

    highlights = data.get("key_highlights", [])
    if isinstance(highlights, list):
        highlights_md = "\n".join(f"- {h}" for h in highlights)
    else:
        highlights_md = f"- {highlights}"

    improvements = data.get("key_areas_for_improvement", [])
    if isinstance(improvements, list) and improvements:
        is_minor = any(
            "no major" in str(item).lower() or "minor suggestion" in str(item).lower()
            for item in improvements
        )
        if is_minor:
            improvements_md = """
**🎉 Outstanding Profile!**  
This resume is well-crafted and does not require major structural changes. The candidate has done an impressive job presenting their experience.
"""
        else:
            improvements_md = "**🔧 Areas for Enhancement:**\n" + "\n".join(f"- {item}" for item in improvements)
    else:
        improvements_md = "**🎉 Excellent Work!** No major improvements needed."

    md = f"""### {emoji} Professional Resume Assessment

**📊 Overall Assessment:** <span style="color: {color}; font-weight: bold;">{overall}</span>  
**🎯 Market Confidence:** <span style="color: {color}; font-weight: bold;">{confidence}</span>

---

#### 💪 Summary of Strengths
{data.get('summary_of_strengths', 'Not provided')}

#### ✨ Standout Highlights
{highlights_md}

#### 💡 Improvement Opportunities
{improvements_md}

#### 🚀 Recommended Career Path
{data.get('suggested_career_path', 'Not provided')}
"""
    return md


def generate_critique(llm, vector_store) -> Tuple[Dict[str, Any], str]:
    """
    Generate professional resume critique.
    
    Returns:
        (critique_data_dict, formatted_markdown_str)
    """
    context = extract_full_resume_context(vector_store)
    if not context:
        raise ValueError("No indexed resume text found. Please upload and index a resume first.")

    critique_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CRITIQUE_PROMPT_TEMPLATE),
            (
                "human",
                "Analyze the resume and provide a professional critique. Respond ONLY with the JSON object in the exact format specified above.",
            ),
        ]
    )

    chain = critique_prompt | llm
    response = chain.invoke({"context": context})

    response_text = response if isinstance(response, str) else getattr(response, "content", str(response))
    critique_data = parse_critique_json(response_text)
    markdown_output = format_critique_markdown(critique_data)

    return critique_data, markdown_output
