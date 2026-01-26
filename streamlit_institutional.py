#!/usr/bin/env python3
"""
Institutional-Grade Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    from institutional_scanner import (
        run_institutional_scan,
        OpportunityRating
    )
    from stockmonitor_enhanced import (
        save_results_to_json,
        save_results_to_csv,
        RESULTS_DIR
    )
except ImportError as e:
    error_msg = str(e)
    if "yfinance" in error_msg.lower():
        st.error("❌ **yfinance Module Not Found**")
        st.markdown("""
        ### 🔧 Fix for Streamlit Cloud:
        
        1. **Check requirements.txt** - Ensure it contains:
           ```
           yfinance>=0.2.28
           ```
        
        2. **Verify file location** - `requirements.txt` must be in the **root directory** of your repository
        
        3. **Redeploy** - After updating requirements.txt:
           - Commit and push to GitHub
           - Streamlit Cloud will automatically reinstall dependencies
        
        4. **Check logs** - In Streamlit Cloud dashboard:
           - Go to Settings → Dependencies
           - Check if yfinance appears in the installed packages
        
        ### 🧪 Test Locally:
        ```bash
        pip install -r requirements.txt
        python -c "import yfinance as yf; print('✅ yfinance works')"
        ```
        """)
        st.code(f"Full error: {error_msg}", language="text")
        st.stop()
    else:
        st.error(f"⚠️ Import error: {e}")
        st.exception(e)
        st.stop()
except RuntimeError as e:
    if "event loop" in str(e).lower():
        st.error("⚠️ Event loop error detected. This is usually caused by ib_insync import.")
        st.info("💡 **Solution:** The scanner should work now. Try running the scan again.")
        st.stop()
    else:
        raise

st.set_page_config(
    page_title="Institutional Scanner Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Get theme styles - CSS-based theme switching
def get_theme_styles(theme):
    if theme == 'dark':
        return """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 1.5rem;
                background: linear-gradient(90deg, #4A90E2, #F5A623);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            [data-testid="stAppViewContainer"] {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            [data-testid="stHeader"] {
                background-color: #1E1E1E;
            }
            .stMetric {
                background-color: #1E1E1E;
                padding: 1rem;
                border-radius: 0.5rem;
                border: 1px solid #333;
            }
            .rating-aaa { background-color: #00AA00; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-aa { background-color: #55CC55; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-a { background-color: #88DD88; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-bbb { background-color: #FFD700; color: black; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-bb { background-color: #FFA500; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-b { background-color: #FF8C00; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-ccc { background-color: #FF6347; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-cc { background-color: #DC143C; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-c { background-color: #B22222; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-d { background-color: #8B0000; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
        """
    else:
        return """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 1.5rem;
                background: linear-gradient(90deg, #1f77b4, #ff7f0e);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            [data-testid="stAppViewContainer"] {
                background-color: #FFFFFF;
                color: #262730;
            }
            .rating-aaa { background-color: #00AA00; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-aa { background-color: #55CC55; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-a { background-color: #88DD88; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-bbb { background-color: #FFD700; color: black; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-bb { background-color: #FFA500; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-b { background-color: #FF8C00; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-ccc { background-color: #FF6347; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-cc { background-color: #DC143C; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-c { background-color: #B22222; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            .rating-d { background-color: #8B0000; color: white; padding: 0.5rem; border-radius: 0.5rem; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
        """

# Apply theme
st.markdown(get_theme_styles(st.session_state.theme), unsafe_allow_html=True)

# Header with theme toggle
col_header, col_theme = st.columns([5, 1])
with col_header:
    st.markdown('<div class="main-header">🏛️ Institutional-Grade Swing Trade Scanner</div>', unsafe_allow_html=True)
with col_theme:
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = "Dark Mode" if st.session_state.theme == 'light' else "Light Mode"
    if st.button(f"{theme_icon} {theme_label}", use_container_width=True):
        toggle_theme()
        st.rerun()

# Sidebar
with st.sidebar:
    st.header("⚙️ Scanner Controls")
    
    max_workers = st.slider("Parallel Workers", 1, 20, 10)
    
    # Removed minimum rating filter - will fetch all results
    
    st.subheader("Actions")
    run_scan = st.button("🚀 Run Institutional Scan", type="primary", use_container_width=True)
    
    st.subheader("Export")
    save_json = st.checkbox("Save to JSON", value=True)
    save_csv = st.checkbox("Save to CSV", value=True)
    
    st.markdown("---")
    st.caption("🏛️ Institutional-Grade Analysis v7.0")

# Session state
if 'institutional_results' not in st.session_state:
    st.session_state.institutional_results = None

# Run scan - fetch ALL results (no minimum rating filter)
if run_scan:
    with st.spinner("🏛️ Running institutional-grade scan... This may take a few minutes..."):
        try:
            # Fetch all results - no minimum rating filter
            all_results, tradeable, non_tradeable, sector_groups = run_institutional_scan(
                max_workers=max_workers,
                min_rating='D'  # Always fetch all results (D is lowest rating)
            )
            # Note: IBKR tradeability check removed - all US stocks assumed tradeable
            
            if save_json:
                save_results_to_json(all_results, f"institutional_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            if save_csv:
                save_results_to_csv(all_results, f"institutional_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            st.session_state.institutional_results = {
                'all': all_results,
                'tradeable': tradeable,
                'non_tradeable': non_tradeable,
                'sector_groups': sector_groups
            }
            
            st.success(f"✅ Scan complete! Found {len(all_results)} total opportunities (all ratings)")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.institutional_results:
    results = st.session_state.institutional_results['all']
    tradeable = st.session_state.institutional_results['tradeable']
    non_tradeable = st.session_state.institutional_results['non_tradeable']
    
    us_results = [r for r in results if r.get('Market') == 'US']
    br_results = [r for r in results if r.get('Market') == 'Brazil']
    
    # Filters Section - Dedicated table for direct filtering (BEFORE summary/metrics)
    st.subheader("🔍 Filters & Visualization Controls")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        min_rating_filter = st.selectbox(
            "Minimum Rating",
            ['All', 'AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D'],
            index=0,
            key="viz_rating"
        )
        min_score_filter = st.slider("Min Rating Score", 0, 100, 0, key="viz_score")
    
    with filter_col2:
        market_filter = st.selectbox(
            "Market",
            ['All', 'US', 'Brazil'],
            index=0,
            key="viz_market"
        )
        sector_filter = st.selectbox(
            "Sector",
            ['All'] + sorted(set(r.get('Sector', 'Unknown') for r in results)),
            index=0,
            key="viz_sector"
        )
    
    with filter_col3:
        min_technical = st.slider("Min Technical Score", 0, 50, 0, key="viz_technical")
        min_fundamental = st.slider("Min Fundamental Score", 0, 30, 0, key="viz_fundamental")
    
    with filter_col4:
        min_momentum = st.slider("Min Momentum Score", 0, 20, 0, key="viz_momentum")
        max_risk = st.slider("Max Risk Score", 0, 20, 20, key="viz_risk")
    
    # Apply filters to results
    filtered_results = results.copy()
    
    if min_rating_filter != 'All':
        rating_order = {'AAA': 10, 'AA': 9, 'A': 8, 'BBB': 7, 'BB': 6, 'B': 5, 
                       'CCC': 4, 'CC': 3, 'C': 2, 'D': 1}
        min_rating_value = rating_order.get(min_rating_filter, 1)
        filtered_results = [r for r in filtered_results 
                           if rating_order.get(r.get('Rating_Grade', 'D'), 1) >= min_rating_value]
    
    filtered_results = [r for r in filtered_results if r.get('Rating_Score', 0) >= min_score_filter]
    
    if market_filter != 'All':
        filtered_results = [r for r in filtered_results if r.get('Market') == market_filter]
    
    if sector_filter != 'All':
        filtered_results = [r for r in filtered_results if r.get('Sector') == sector_filter]
    
    filtered_results = [r for r in filtered_results if r.get('Technical_Score', 0) >= min_technical]
    filtered_results = [r for r in filtered_results if r.get('Fundamental_Score', 0) >= min_fundamental]
    filtered_results = [r for r in filtered_results if r.get('Momentum_Score', 0) >= min_momentum]
    filtered_results = [r for r in filtered_results if r.get('Risk_Score', 0) <= max_risk]
    
    # Display filter summary
    st.info(f"📊 Showing {len(filtered_results)} of {len(results)} opportunities (after filters applied)")
    
    st.markdown("---")
    
    # Summary metrics - show both total and filtered
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Opportunities", len(results), delta=f"{len(filtered_results)} filtered")
    with col2:
        aaa_count = len([r for r in results if r.get('Rating_Grade') == 'AAA'])
        st.metric("AAA Rated", aaa_count, delta=f"{len([r for r in results if r.get('Rating_Grade') in ['AAA', 'AA', 'A']])} A+")
    with col3:
        st.metric("US Stocks", len(us_results))
    with col4:
        st.metric("BR Stocks", len(br_results))
    with col5:
        st.metric("Tradeable", len(tradeable))
    with col6:
        avg_score = sum(r.get('Rating_Score', 0) for r in results) / len(results) if results else 0
        st.metric("Avg Rating Score", f"{avg_score:.1f}")
    
    # Rating distribution - show both total and filtered
    st.subheader("📊 Rating Distribution")
    rating_counts = pd.Series([r.get('Rating_Grade', 'D') for r in filtered_results]).value_counts().sort_index()
    
    col_chart, col_stats = st.columns([2, 1])
    
    with col_chart:
        if len(rating_counts) > 0:
            # Convert to DataFrame format for Plotly Express
            rating_df = pd.DataFrame({
                'Rating': rating_counts.index,
                'Count': rating_counts.values
            })
            
            fig_rating = px.bar(
                rating_df,
                x='Rating',
                y='Count',
                title='Opportunities by Rating Grade (Filtered)',
                labels={'Rating': 'Rating Grade', 'Count': 'Count'},
                color='Count',
                color_continuous_scale='RdYlGn'
            )
            fig_rating.update_layout(showlegend=False)
            st.plotly_chart(fig_rating, use_container_width=True)
        else:
            st.info("No rating data available. Adjust filters to see results.")
    
    with col_stats:
        st.subheader("Rating Breakdown (Filtered)")
        if len(filtered_results) > 0:
            for grade in ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D']:
                count = len([r for r in filtered_results if r.get('Rating_Grade') == grade])
                total_count = len([r for r in results if r.get('Rating_Grade') == grade])
                if total_count > 0:
                    st.metric(grade, count, delta=f"{total_count} total")
        else:
            st.info("No results to display")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏆 Top Opportunities",
        "📊 By Sector",
        "🇺🇸 US Market",
        "🇧🇷 Brazil Market",
        "📈 Analysis",
        "⚙️ Details"
    ])
    
    with tab1:
        st.subheader("🏆 Top Institutional Opportunities")
        
        # Use filtered_results from main filters section
        # Sort by rating score
        sorted_filtered = sorted(filtered_results, key=lambda x: x.get('Rating_Score', 0), reverse=True)
        
        # Display top opportunities
        for i, r in enumerate(sorted_filtered[:20], 1):
            grade = r.get('Rating_Grade', 'D')
            score = r.get('Rating_Score', 0)
            
            with st.expander(f"#{i} {r['Ticker']} - {grade} ({score:.1f}/100) - {r.get('Company', 'N/A')}"):
                col_info, col_scores = st.columns([2, 1])
                
                with col_info:
                    st.write(f"**Recommendation:** {r.get('Recommendation', 'N/A')}")
                    st.write(f"**Market:** {r.get('Market', 'N/A')} | **Sector:** {r.get('Sector', 'N/A')}")
                    st.write(f"**Price:** ${r.get('Close', 0):.2f} | **Change:** {r.get('Change%', 0):+.2f}%")
                    st.write(f"**Market Regime:** {r.get('Market_Regime', 'N/A')} ({r.get('Regime_Confidence', 0):.1f}% confidence)")
                
                with col_scores:
                    st.metric("Technical", f"{r.get('Technical_Score', 0):.1f}/50")
                    st.metric("Fundamental", f"{r.get('Fundamental_Score', 0):.1f}/30")
                    st.metric("Momentum", f"{r.get('Momentum_Score', 0):.1f}/20")
                    st.metric("Risk", f"{r.get('Risk_Score', 0):.1f}/20")
                
                # Strengths and Risks
                col_str, col_risk = st.columns(2)
                with col_str:
                    st.subheader("✅ Key Strengths")
                    for strength in r.get('Key_Strengths', [])[:5]:
                        st.write(f"• {strength}")
                
                with col_risk:
                    st.subheader("⚠️ Key Risks")
                    for risk in r.get('Key_Risks', [])[:5]:
                        st.write(f"• {risk}")
                
                # Technical indicators
                st.subheader("📊 Technical Indicators")
                tech_cols = st.columns(7)
                tech_indicators = {
                    'RSI': r.get('RSI'),
                    'MACD': r.get('MACD'),
                    'ADX': r.get('ADX'),
                    'Stoch K': r.get('Stoch_K'),
                    'MFI': r.get('MFI'),
                    'VWAP': r.get('VWAP'),
                    'Williams %R': r.get('Williams_R')
                }
                
                # Add VWAP distance if available
                if r.get('VWAP_Distance%') is not None:
                    vwap_dist = r.get('VWAP_Distance%', 0)
                    vwap_emoji = "🟢" if vwap_dist > 0 else "🔴" if vwap_dist < -2 else "🟡"
                    st.caption(f"{vwap_emoji} VWAP Distance: {vwap_dist:+.2f}% (Price vs VWAP)")
                for i, (name, value) in enumerate(tech_indicators.items()):
                    if value is not None:
                        tech_cols[i].metric(name, f"{value:.1f}")
    
    with tab2:
        st.subheader("📊 Opportunities by Sector")
        
        if st.session_state.institutional_results and 'sector_groups' in st.session_state.institutional_results:
            sector_groups = st.session_state.institutional_results['sector_groups']
            
            # Filter sector groups by current filters
            filtered_sector_groups = {}
            for sector, opps in sector_groups.items():
                filtered_opps = [o for o in opps if o in filtered_results]
                if filtered_opps:
                    filtered_sector_groups[sector] = filtered_opps
            
            # Sector selector
            sectors = sorted(filtered_sector_groups.keys())
            selected_sector = st.selectbox("Select Sector", ['All Sectors'] + sectors)
            
            if selected_sector == 'All Sectors':
                # Show all sectors with summary (filtered)
                st.subheader("Sector Summary (Filtered)")
                
                sector_summary = []
                for sector, opps in sorted(filtered_sector_groups.items(), key=lambda x: len(x[1]), reverse=True):
                    avg_score = sum(o.get('Rating_Score', 0) for o in opps) / len(opps) if opps else 0
                    top_grade = max([o.get('Rating_Grade', 'D') for o in opps], key=lambda x: ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D'].index(x)) if opps else 'D'
                    sector_summary.append({
                        'Sector': sector,
                        'Count': len(opps),
                        'Avg Score': round(avg_score, 1),
                        'Top Grade': top_grade,
                        'Top Ticker': opps[0]['Ticker'] if opps else 'N/A'
                    })
                
                df_summary = pd.DataFrame(sector_summary)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)
                
                # Show top opportunities from each sector
                st.subheader("Top Opportunities by Sector")
                for sector, opps in sorted(sector_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                    with st.expander(f"{sector} ({len(opps)} opportunities)"):
                        top_3 = opps[:3]
                        for opp in top_3:
                            st.write(f"**{opp['Ticker']}** - {opp.get('Rating_Grade', 'D')} ({opp.get('Rating_Score', 0):.1f}) | "
                                   f"${opp.get('Close', 0):.2f} | {opp.get('Change%', 0):+.2f}%")
            else:
                # Show opportunities for selected sector (filtered)
                if selected_sector in filtered_sector_groups:
                    opps = filtered_sector_groups[selected_sector]
                    st.write(f"**{len(opps)} opportunities in {selected_sector}**")
                    
                    # Display table
                    df_sector = pd.DataFrame(opps)
                    display_cols = ['Ticker', 'Company', 'Rating_Grade', 'Rating_Score',
                                  'Technical_Score', 'Fundamental_Score', 'Momentum_Score',
                                  'Close', 'Change%', 'Week%', 'VWAP', 'VWAP_Distance%']
                    
                    # Filter columns that exist
                    available_cols = [col for col in display_cols if col in df_sector.columns]
                    
                    st.dataframe(
                        df_sector[available_cols].sort_values('Rating_Score', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(f"No opportunities found for {selected_sector}")
        else:
            st.info("Run a scan to see sector breakdown")
    
    with tab3:
        st.subheader("🇺🇸 US Market Opportunities")
        
        # Filter US results
        us_filtered = [r for r in filtered_results if r.get('Market') == 'US']
        
        if us_filtered:
            df_us = pd.DataFrame(us_filtered)
            
            # Display table
            display_cols = ['Ticker', 'Company', 'Rating_Grade', 'Rating_Score', 
                          'Technical_Score', 'Fundamental_Score', 'Momentum_Score',
                          'Close', 'Change%', 'Week%', 'Market_Regime']
            
            st.dataframe(
                df_us[display_cols].sort_values('Rating_Score', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No US market results")
    
    with tab4:
        st.subheader("🇧🇷 Brazil Market Opportunities")
        
        # Filter BR results
        br_filtered = [r for r in filtered_results if r.get('Market') == 'Brazil']
        
        if br_filtered:
            df_br = pd.DataFrame(br_filtered)
            
            display_cols = ['Ticker', 'Company', 'Rating_Grade', 'Rating_Score',
                          'Technical_Score', 'Fundamental_Score', 'Momentum_Score',
                          'Close', 'Close_USD', 'Change%', 'Week%', 'Market_Regime']
            
            st.dataframe(
                df_br[display_cols].sort_values('Rating_Score', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No Brazil market results")
    
    with tab5:
        st.subheader("📈 Comprehensive Analysis")
        
        if filtered_results:
            df = pd.DataFrame(filtered_results)
            
            # Score vs Risk scatter
            fig_scatter = px.scatter(
                df,
                x='Risk_Score',
                y='Rating_Score',
                color='Rating_Grade',
                size='Technical_Score',
                hover_data=['Ticker', 'Company', 'Market'],
                title='Opportunity Score vs Risk',
                labels={'Risk_Score': 'Risk Score (Lower is Better)', 
                       'Rating_Score': 'Opportunity Score'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Component scores
            col1, col2 = st.columns(2)
            
            with col1:
                fig_components = go.Figure()
                fig_components.add_trace(go.Bar(
                    name='Technical',
                    x=df['Ticker'].head(10),
                    y=df['Technical_Score'].head(10)
                ))
                fig_components.add_trace(go.Bar(
                    name='Fundamental',
                    x=df['Ticker'].head(10),
                    y=df['Fundamental_Score'].head(10)
                ))
                fig_components.add_trace(go.Bar(
                    name='Momentum',
                    x=df['Ticker'].head(10),
                    y=df['Momentum_Score'].head(10)
                ))
                fig_components.update_layout(
                    title='Score Components (Top 10)',
                    barmode='stack',
                    height=400
                )
                st.plotly_chart(fig_components, use_container_width=True)
            
            with col2:
                # Market regime distribution
                regime_counts = df['Market_Regime'].value_counts()
                fig_regime = px.pie(
                    values=regime_counts.values,
                    names=regime_counts.index,
                    title='Market Regime Distribution'
                )
                st.plotly_chart(fig_regime, use_container_width=True)
    
    with tab6:
        st.subheader("⚙️ Scanner Details")
        
        st.info("""
        **Institutional-Grade Features:**
        - ✅ Comprehensive Technical Analysis (20+ indicators)
        - ✅ Fundamental Analysis (Valuation, Profitability, Growth)
        - ✅ Momentum Analysis
        - ✅ Risk Metrics (Sharpe, Sortino, Max Drawdown)
        - ✅ Market Regime Detection
        - ✅ Opportunity Rating System (AAA to D)
        - ✅ Brazil Market Support with Currency Conversion
        
        **Rating System:**
        - **AAA-AA**: Exceptional/Strong Buy opportunities
        - **A-BBB**: Good/Moderate Buy opportunities
        - **BB-B**: Watch/Cautious opportunities
        - **CCC-D**: Avoid opportunities
        """)
        
        if st.button("💾 Export All Results"):
            if results:
                json_file = save_results_to_json(results, f"institutional_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                csv_file = save_results_to_csv(results, f"institutional_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                st.success(f"✅ Exported to {json_file} and {csv_file}")

else:
    st.info("👆 Click 'Run Institutional Scan' in the sidebar to start scanning")

# Add README/About section as a new tab or expandable section
st.markdown("---")
with st.expander("📖 README - Scoring System & KPIs", expanded=False):
    st.markdown("""
    # 🏛️ Institutional-Grade Scoring System
    
    ## 🎯 Opportunity Rating System
    
    Our scanner uses a comprehensive **AAA to D rating system** based on institutional-grade analysis:
    
    | Grade | Score Range | Recommendation | Description |
    |-------|------------|----------------|-------------|
    | **AAA** | 90-100 | EXCEPTIONAL BUY | Highest Quality Opportunity |
    | **AA** | 85-89 | STRONG BUY | High Quality Opportunity |
    | **A** | 80-84 | BUY | Good Quality Opportunity |
    | **BBB** | 75-79 | MODERATE BUY | Above Average Opportunity |
    | **BB** | 70-74 | WATCH | Average Opportunity |
    | **B** | 65-69 | CAUTIOUS | Below Average Opportunity |
    | **CCC** | 60-64 | AVOID | Poor Quality |
    | **CC** | 55-59 | AVOID | Very Poor Quality |
    | **C** | 50-54 | AVOID | Extremely Poor Quality |
    | **D** | 0-49 | AVOID | Default Quality |
    
    ---
    
    ## 📊 Scoring Components (Total: 100 points)
    
    ### 1. Technical Analysis (50 points - 50% weight)
    
    **Moving Averages:**
    - SMA 20, 50, 200
    - Golden Cross detection
    - Price position relative to MAs
    
    **Momentum Indicators:**
    - **RSI** (Relative Strength Index): Overbought/oversold conditions
    - **MACD**: Trend and momentum crossover
    - **Stochastic Oscillator**: %K and %D lines
    - **Williams %R**: Momentum oscillator
    - **CCI** (Commodity Channel Index): Cyclical trends
    - **MFI** (Money Flow Index): Volume-weighted RSI
    
    **Trend Indicators:**
    - **ADX** (Average Directional Index): Trend strength (0-100)
    - **Aroon Indicator**: Trend direction and strength
    - **Ichimoku Cloud**: Comprehensive trend analysis
    
    **Volume Analysis:**
    - **Volume Ratio**: Current vs average volume
    - **OBV** (On-Balance Volume): Volume flow direction
    - **VWAP** (Volume Weighted Average Price): Institutional reference price
    
    **Support/Resistance:**
    - Automatic pivot point detection
    - Fibonacci retracement levels
    - Distance to key levels
    
    **Chart Patterns:**
    - Double Bottom
    - Head & Shoulders
    - Ascending Triangle
    
    ---
    
    ### 2. Fundamental Analysis (30 points - 30% weight)
    
    **Valuation Metrics:**
    - **P/E Ratio**: Price-to-Earnings (lower is better for value)
    - **P/B Ratio**: Price-to-Book (lower is better)
    - **Forward P/E**: Future earnings expectations
    
    **Profitability:**
    - **Profit Margins**: Net profit margin percentage
    - **ROE** (Return on Equity): Shareholder returns (>15% is good)
    - **ROA** (Return on Assets): Asset efficiency (>10% is good)
    
    **Growth Metrics:**
    - **Revenue Growth**: Year-over-year revenue growth
    - **Earnings Growth**: Year-over-year earnings growth
    - **Forward P/E vs Current P/E**: Earnings growth expectations
    
    **Financial Health:**
    - **Debt/Equity Ratio**: Leverage assessment (<50 is good)
    - **Current Ratio**: Liquidity measure (>2.0 is strong)
    
    **Market Position:**
    - **Institutional Ownership**: % held by institutions (>70% is high)
    - **Analyst Recommendations**: Buy/Hold/Sell consensus
    - **Market Capitalization**: Company size classification
    
    ---
    
    ### 3. Momentum Analysis (20 points - 20% weight)
    
    - **Weekly Price Change**: Short-term momentum
    - **Monthly Price Change**: Medium-term momentum
    - **Rate of Change (ROC)**: 10-day and 20-day momentum
    - **Relative Strength**: Performance vs market (SPY)
    - **Price Momentum Indicators**: Trend acceleration
    
    ---
    
    ### 4. Risk Assessment (20 points - lower is better)
    
    - **ATR%** (Average True Range): Volatility measure
    - **Maximum Drawdown**: Largest peak-to-trough decline
    - **Sharpe Ratio**: Risk-adjusted returns (>1.0 is good)
    - **Sortino Ratio**: Downside risk-adjusted returns
    - **Beta**: Market correlation and volatility
    - **Calmar Ratio**: Return vs max drawdown
    
    **Risk Adjustment:**
    - Total score is adjusted by risk: `adjusted_score = total_score × (1 - risk_score/20)`
    - Higher risk = lower adjusted score
    
    ---
    
    ## 🔍 Key Performance Indicators (KPIs)
    
    ### Technical KPIs
    - **RSI**: 30-70 range is healthy, <30 oversold, >70 overbought
    - **ADX**: >25 indicates strong trend
    - **Volume Ratio**: >1.5 indicates high interest
    - **VWAP Distance**: Price above VWAP is bullish
    
    ### Fundamental KPIs
    - **P/E Ratio**: Compare to sector average
    - **ROE**: >20% is excellent, >15% is good
    - **Debt/Equity**: <50 is conservative, >100 is risky
    - **Current Ratio**: >2.0 indicates strong liquidity
    
    ### Risk KPIs
    - **ATR%**: <5% is low volatility, >8% is high
    - **Sharpe Ratio**: >1.0 indicates good risk-adjusted returns
    - **Max Drawdown**: <20% is acceptable, >30% is concerning
    
    ---
    
    ## 🎯 How to Use the Filters
    
    Use the **Filters Table** below to:
    1. Filter by **Rating Grade** (AAA to D)
    2. Set **Minimum Score** threshold
    3. Filter by **Market** (US or Brazil)
    4. Filter by **Sector**
    5. Apply **Technical/Fundamental/Momentum** score filters
    6. Filter by **Risk Level**
    
    All filters work together to help you find the best opportunities!
    """)

st.markdown("---")
st.caption("🏛️ Institutional-Grade Scanner v7.0 | Professional Analysis")
