"""
Custom CSS styles and theme definitions for Streamlit UI.
Includes dedicated styles for ATS Checker, Score Meters, Keyword Badges,
Before/After rewrites, and Score Boost Action Cards.
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Header Banner */
    .hero-banner {
        text-align: center;
        padding: 28px 24px;
        background: linear-gradient(135deg, #f0f7ff 0%, #e0effe 100%);
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin: 0 0 8px 0;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: #475569;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.4;
        margin: 0;
    }

    /* Badges */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 12px;
        flex-wrap: wrap;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .badge-blue {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }

    .badge-green {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }

    .badge-purple {
        background-color: #f3e8ff;
        color: #6b21a8;
        border: 1px solid #e9d5ff;
    }

    .badge-amber {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .badge-red {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }

    /* Content Cards */
    .info-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .info-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }

    /* Metric Tiles */
    .stat-tile {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .stat-label {
        font-size: 0.78rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .stat-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }

    /* ATS Score Comparison Hero */
    .score-comparison-banner {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 24px 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .score-col-box {
        text-align: center;
        flex: 1;
    }

    .score-big-number {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.03em;
    }

    .score-col-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        color: #94a3b8;
        margin-top: 6px;
    }

    .score-arrow {
        font-size: 2.2rem;
        color: #64748b;
        padding: 0 12px;
    }

    .score-gain-badge {
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 8px;
    }

    /* Action Roadmap Card */
    .action-step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }

    .action-step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }

    .action-step-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }

    /* Keyword Tags */
    .keyword-pill {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    .keyword-pill-green {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }

    .keyword-pill-amber {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .keyword-pill-blue {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }

    /* Comparison Card */
    .rewrite-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    .before-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        color: #7f1d1d;
        font-size: 0.95rem;
    }

    .after-box {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        color: #064e3b;
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* Critique Card */
    .critique-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        line-height: 1.6;
    }

    /* Point Deduction Category Card */
    .deduction-category-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 22px 14px 22px;
        margin-bottom: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }

    .deduction-cat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .deduction-cat-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #0f172a;
    }

    .deduction-progress-track {
        width: 100%;
        height: 12px;
        background: #f1f5f9;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 4px;
    }

    .deduction-progress-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.4s ease;
    }

    .deduction-progress-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
    }

    /* Individual Deduction Row */
    .deduction-row {
        background: #fff8f8;
        border: 1px solid #fecaca;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .deduction-row-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
        gap: 12px;
    }

    .deduction-issue {
        font-size: 0.95rem;
        font-weight: 700;
        color: #991b1b;
        flex: 1;
    }

    .deduction-pts-badge {
        background: #fee2e2;
        color: #dc2626;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 800;
        white-space: nowrap;
        border: 1px solid #fca5a5;
    }

    .deduction-fix {
        font-size: 0.9rem;
        color: #065f46;
        background: #ecfdf5;
        border-left: 3px solid #10b981;
        padding: 8px 12px;
        border-radius: 0 8px 8px 0;
        line-height: 1.5;
    }

    /* Summary Table */
    .deduction-summary-table {
        background: linear-gradient(135deg, #f8fafc 0%, #f0f4ff 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 8px;
    }

    .deduction-summary-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
    }

    .deduction-summary-label {
        font-size: 1rem;
        font-weight: 700;
        color: #334155;
    }

    .deduction-summary-value {
        font-size: 1.15rem;
        font-weight: 800;
    }

    /* Buttons */
    div.stButton > button {
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
    }
</style>
"""
