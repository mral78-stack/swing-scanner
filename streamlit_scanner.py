#!/usr/bin/env python3
"""
Streamlit Dashboard for Enhanced Swing Trade Scanner
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

# Add parent directory to path to import scanner modules
sys.path.append(str(Path(__file__).parent))

# Import enhanced scanner
try:
    from stockmonitor_enhanced import (
        run_scanner_analysis_parallel,
        save_results_to_json,
        save_results_to_csv,
        commit_and_push_results,
        setup_git_repo,
        RESULTS_DIR
    )
except ImportError:
    st.error("⚠️ Could not import enhanced scanner. Make sure stockmonitor_enhanced.py is in the same directory.")
    st.stop()

# Page config
st.set_page_config(
    page_title="Swing Trade Scanner Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stDataFrame {
        font-size: 0.9rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📈 Enhanced Swing Trade Scanner Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Scanner settings
    st.subheader("Scanner Settings")
    max_workers = st.slider("Parallel Workers", 1, 20, 10, help="Number of parallel workers for scanning")
    min_score = st.slider("Minimum Score", 0, 100, 30, help="Minimum score to display")
    
    # Action buttons
    st.subheader("Actions")
    run_scan = st.button("🚀 Run Scanner", type="primary", use_container_width=True)
    refresh_data = st.button("🔄 Refresh Data", use_container_width=True)
    
    # Save options
    st.subheader("Export Options")
    save_json = st.checkbox("Save to JSON", value=True)
    save_csv = st.checkbox("Save to CSV", value=True)
    
    # GitHub options
    st.subheader("GitHub Integration")
    github_push = st.checkbox("Push to GitHub", value=False)
    github_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo.git")
    
    st.markdown("---")
    st.caption("v6.0 - Enhanced Scanner with Parallel Processing")

# Initialize session state
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None
if 'scan_time' not in st.session_state:
    st.session_state.scan_time = None
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None

# Load existing results
@st.cache_data(ttl=3600)
def load_latest_results():
    """Load latest scan results from files"""
    if not os.path.exists(RESULTS_DIR):
        return None
    
    json_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')], reverse=True)
    if json_files:
        latest_file = os.path.join(RESULTS_DIR, json_files[0])
        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

# Run scanner
if run_scan:
    with st.spinner("🔍 Scanning stocks... This may take a few minutes..."):
        try:
            all_results, tradeable_results, non_tradeable_results = run_scanner_analysis_parallel(
                max_workers=max_workers
            )
            
            # Filter by min score
            filtered_results = [r for r in all_results if r['Score'] >= min_score]
            
            # Save results
            if save_json:
                save_results_to_json(filtered_results)
            
            if save_csv:
                save_results_to_csv(filtered_results)
            
            # GitHub push
            if github_push and github_url:
                setup_git_repo(remote_url=github_url)
                commit_and_push_results()
            
            st.session_state.scan_results = {
                'all': filtered_results,
                'tradeable': tradeable_results,
                'non_tradeable': non_tradeable_results
            }
            st.session_state.scan_time = datetime.now()
            st.session_state.last_scan = filtered_results
            
            st.success(f"✅ Scan complete! Found {len(filtered_results)} opportunities")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error running scanner: {str(e)}")
            st.exception(e)

# Load cached results if available
if st.session_state.scan_results is None:
    cached_results = load_latest_results()
    if cached_results:
        st.session_state.scan_results = {
            'all': cached_results,
            # IBKR tradeability removed - all US stocks assumed tradeable
            'tradeable': [r for r in cached_results if r.get('Market') == 'US'],
            'non_tradeable': [r for r in cached_results if r.get('Market') == 'Brazil']
        }
        st.info("📊 Displaying cached results. Click 'Run Scanner' for fresh data.")

# Display results
if st.session_state.scan_results:
    results = st.session_state.scan_results['all']
    tradeable = st.session_state.scan_results['tradeable']
    non_tradeable = st.session_state.scan_results['non_tradeable']
    
    # Filter by market
    us_results = [r for r in results if r.get('Market') == 'US']
    br_results = [r for r in results if r.get('Market') == 'Brazil']
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Opportunities", len(results))
    with col2:
        st.metric("US Stocks", len(us_results))
    with col3:
        st.metric("BR Stocks", len(br_results))
    with col4:
        st.metric("Tradeable", len(tradeable))
    with col5:
        avg_score = sum(r['Score'] for r in results) / len(results) if results else 0
        st.metric("Avg Score", f"{avg_score:.1f}")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🇺🇸 US Market", 
        "🇧🇷 Brazil Market", 
        "📈 Charts", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.subheader("Top Opportunities")
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        if not df.empty:
            # Score distribution chart
            col_chart, col_table = st.columns([2, 1])
            
            with col_chart:
                fig_score = px.histogram(
                    df, 
                    x='Score', 
                    nbins=30,
                    title='Score Distribution',
                    labels={'Score': 'Scanner Score', 'count': 'Number of Stocks'}
                )
                st.plotly_chart(fig_score, use_container_width=True)
            
            with col_table:
                st.subheader("Score Stats")
                st.metric("Max Score", f"{df['Score'].max():.0f}")
                st.metric("Min Score", f"{df['Score'].min():.0f}")
                st.metric("Median", f"{df['Score'].median():.0f}")
            
            # Top 20 table
            st.subheader("Top 20 Opportunities")
            top_20 = df.nlargest(20, 'Score')[
                ['Ticker', 'Company', 'Market', 'Sector', 'Close', 'Change%', 
                 'Week%', 'Score', 'Rating', 'RSI', 'Volume_Ratio']
            ]
            st.dataframe(top_20, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("🇺🇸 US Market Opportunities")
        
        if us_results:
            df_us = pd.DataFrame(us_results)
            
            # Filters
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                sectors = ['All'] + sorted(df_us['Sector'].unique().tolist())
                selected_sector = st.selectbox("Filter by Sector", sectors)
            with col_filter2:
                min_score_filter = st.slider("Min Score", 0, 100, min_score, key="us_score")
            with col_filter3:
                tradeable_only = st.checkbox("Tradeable Only", value=False)
            
            # Apply filters
            filtered_us = df_us[df_us['Score'] >= min_score_filter]
            if selected_sector != 'All':
                filtered_us = filtered_us[filtered_us['Sector'] == selected_sector]
            if tradeable_only:
                # IBKR tradeability filter removed - all US stocks shown
                pass
            
            # Display
            st.dataframe(
                filtered_us[
                    ['Ticker', 'Company', 'Sector', 'Close', 'Change%', 'Week%', 
                     'Score', 'Rating', 'RSI', 'ADX', 'Volume_Ratio']
                ].sort_values('Score', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Sector breakdown
            st.subheader("Sector Breakdown")
            sector_counts = df_us.groupby('Sector').agg({
                'Ticker': 'count',
                'Score': 'mean'
            }).sort_values('Score', ascending=False)
            sector_counts.columns = ['Count', 'Avg Score']
            st.dataframe(sector_counts, use_container_width=True)
        else:
            st.info("No US market results available")
    
    with tab3:
        st.subheader("🇧🇷 Brazil Market Opportunities")
        
        if br_results:
            df_br = pd.DataFrame(br_results)
            
            # Filters
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                sectors_br = ['All'] + sorted(df_br['Sector'].unique().tolist())
                selected_sector_br = st.selectbox("Filter by Sector", sectors_br, key="br_sector")
            with col_filter2:
                min_score_filter_br = st.slider("Min Score", 0, 100, min_score, key="br_score")
            
            # Apply filters
            filtered_br = df_br[df_br['Score'] >= min_score_filter_br]
            if selected_sector_br != 'All':
                filtered_br = filtered_br[filtered_br['Sector'] == selected_sector_br]
            
            # Display
            st.dataframe(
                filtered_br[
                    ['Ticker', 'Company', 'Sector', 'Close', 'Change%', 'Week%', 
                     'Score', 'Rating', 'RSI', 'ADX', 'Volume_Ratio']
                ].sort_values('Score', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Sector breakdown
            st.subheader("Sector Breakdown")
            sector_counts_br = df_br.groupby('Sector').agg({
                'Ticker': 'count',
                'Score': 'mean'
            }).sort_values('Score', ascending=False)
            sector_counts_br.columns = ['Count', 'Avg Score']
            st.dataframe(sector_counts_br, use_container_width=True)
        else:
            st.info("No Brazil market results available")
    
    with tab4:
        st.subheader("📈 Visualizations")
        
        if results:
            df = pd.DataFrame(results)
            
            # Score vs RSI scatter
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scatter = px.scatter(
                    df,
                    x='RSI',
                    y='Score',
                    color='Market',
                    size='Volume_Ratio',
                    hover_data=['Ticker', 'Company', 'Sector'],
                    title='Score vs RSI by Market',
                    labels={'RSI': 'RSI', 'Score': 'Scanner Score'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    df,
                    x='Market',
                    y='Score',
                    color='Market',
                    title='Score Distribution by Market',
                    labels={'Market': 'Market', 'Score': 'Scanner Score'}
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Sector performance
            if 'Sector' in df.columns:
                sector_scores = df.groupby('Sector')['Score'].mean().sort_values(ascending=False).head(15)
                fig_sector = px.bar(
                    x=sector_scores.index,
                    y=sector_scores.values,
                    title='Average Score by Sector (Top 15)',
                    labels={'x': 'Sector', 'y': 'Average Score'}
                )
                fig_sector.update_xaxes(tickangle=45)
                st.plotly_chart(fig_sector, use_container_width=True)
    
    with tab5:
        st.subheader("⚙️ Scanner Configuration")
        
        st.info("""
        **Enhanced Scanner Features:**
        - ✅ Parallel processing for faster scans
        - ✅ Advanced technical indicators (Stochastic, ADX, Support/Resistance)
        - ✅ Chart pattern detection
        - ✅ Volume profile analysis
        - ✅ Data persistence (JSON/CSV)
        - ✅ GitHub integration
        - ✅ Real-time dashboard
        
        **Technical Indicators:**
        - RSI, MACD, Stochastic
        - ADX (trend strength)
        - Support/Resistance levels
        - Volume Profile (POC)
        - On-Balance Volume (OBV)
        - Bollinger Bands
        - Chart patterns
        """)
        
        if st.session_state.scan_time:
            st.caption(f"Last scan: {st.session_state.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Export current results
        st.subheader("Export Current Results")
        if st.button("💾 Export to JSON"):
            if results:
                filename = save_results_to_json(results)
                st.success(f"✅ Saved to {filename}")
        
        if st.button("💾 Export to CSV"):
            if results:
                filename = save_results_to_csv(results)
                st.success(f"✅ Saved to {filename}")

else:
    st.info("👆 Click 'Run Scanner' in the sidebar to start scanning stocks")

# Footer
st.markdown("---")
st.caption("🤖 Enhanced Swing Trade Scanner v6.0 | Built with Streamlit")
