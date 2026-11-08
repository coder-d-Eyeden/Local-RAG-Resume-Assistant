"""
Custom CSS styles and theme definitions for Streamlit UI.
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

    /* Critique Card */
    .critique-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        line-height: 1.6;
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

