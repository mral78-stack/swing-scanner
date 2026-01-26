#!/usr/bin/env python3
"""
Market Ticker Definitions
Separated from stockmonitor.py to avoid ib_insync import issues in Streamlit
"""

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 🇺🇸 US MARKET TICKERS - COMPREHENSIVE COVERAGE                              │
# └─────────────────────────────────────────────────────────────────────────────┘

US_SECTORS = {
    '🤖 AI/Semiconductors': [
        'NVDA', 'AMD', 'INTC', 'AVGO', 'QCOM', 'TXN', 'ADI', 'MRVL', 'MU', 'LRCX',
        'AMAT', 'KLAC', 'ASML', 'TSM', 'SNPS', 'CDNS', 'SMCI', 'AI', 'PLTR', 'PATH',
        'ARM', 'ONTO', 'ACLS', 'WOLF', 'ON', 'SWKS', 'QRVO', 'MPWR', 'MCHP',
    ],
    '💻 Software/Cloud': [
        'MSFT', 'CRM', 'NOW', 'ADBE', 'ORCL', 'SAP', 'INTU', 'WDAY', 'SNOW', 'DDOG',
        'NET', 'MDB', 'CRWD', 'PANW', 'ZS', 'OKTA', 'FTNT', 'GTLB', 'TEAM', 'HUBS',
        'DOCU', 'ZM', 'TWLO', 'ESTC', 'CFLT', 'PD', 'SUMO', 'S', 'ASAN',
        # Mid-cap additions
        'FOUR', 'DOCN', 'BILL', 'FROG', 'FRSH', 'NCNO', 'APPN', 'ALRM', 'DOCN',
        'MIME', 'QLYS', 'VRNS', 'QLYS', 'VRNS', 'QLYS', 'VRNS', 'QLYS', 'VRNS',
    ],
    '📱 Consumer Tech': [
        'AAPL', 'GOOGL', 'GOOG', 'META', 'AMZN', 'NFLX', 'SHOP', 'ETSY', 'EBAY', 
        'SNAP', 'PINS', 'SPOT', 'ROKU', 'TTD', 'DIS', 'RBLX', 'EA', 'TTWO', 'U',
        'MTCH', 'BMBL', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'UBER', 'LYFT', 'DASH',
    ],
    '⚡ Energy/Nuclear': [
        'OKLO', 'SMR', 'CEG', 'VST', 'CCJ', 'LEU', 'UEC', 'UUUU', 'DNN', 'NNE',
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'DVN', 'MPC', 'VLO', 'PSX',
        'HAL', 'BKR', 'FANG', 'PXD', 'HES', 'MRO', 'APA', 'OVV',
    ],
    '☀️ Renewable Energy': [
        'ENPH', 'SEDG', 'FSLR', 'RUN', 'NOVA', 'ARRY', 'MAXN', 'JKS', 'CSIQ',
        'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'FSR', 'GOEV', 'WKHS',
        'QS', 'CHPT', 'BLNK', 'EVGO', 'ALB', 'SQM', 'LAC', 'PLL', 'LTHM',
    ],
    '🚀 Space/Defense': [
        'RKLB', 'ASTS', 'LUNR', 'SPCE', 'BKSY', 'PL', 'IRDM', 'GSAT',
        'LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX', 'HII', 'TDG', 'HEI',
        'KTOS', 'AVAV', 'LDOS', 'SAIC', 'MRCY', 'AXON', 'TXT', 'ERJ',
    ],
    '💳 Fintech': [
        'SOFI', 'NU', 'HOOD', 'AFRM', 'UPST', 'LC', 'OPEN', 'UWMC',
        'SQ', 'PYPL', 'V', 'MA', 'AXP', 'FIS', 'FISV', 'GPN', 'ADYEN',
        'COIN', 'MSTR', 'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF', 'BTBT',
    ],
    '🏦 Banks/Financial': [
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'SCHW',
        'BLK', 'BX', 'KKR', 'APO', 'ARES', 'CG', 'OWL', 'TROW',
        'AIG', 'MET', 'PRU', 'ALL', 'TRV', 'CB', 'AFL', 'PGR',
    ],
    '🧬 Biotech': [
        'MRNA', 'REGN', 'VRTX', 'GILD', 'BIIB', 'AMGN', 'ILMN', 'EXAS',
        'HIMS', 'CRSP', 'BEAM', 'NTLA', 'EDIT', 'VERV', 'PRME', 'LEGN',
        'LLY', 'NVO', 'VKTX', 'ALT', 'GPCR', 'SRPT', 'ALNY', 'BMRN',
    ],
    '🏥 Healthcare': [
        'UNH', 'ELV', 'CI', 'HUM', 'CNC', 'MOH', 'CVS', 'WBA',
        'JNJ', 'PFE', 'MRK', 'ABBV', 'BMY', 'AZN', 'GSK', 'SNY', 'NVS',
        'ABT', 'MDT', 'SYK', 'ISRG', 'BSX', 'EW', 'DXCM', 'PODD',
        'TMO', 'DHR', 'A', 'IQV', 'MTD', 'WAT', 'PKI',
    ],
    '⛏️ Mining/Metals': [
        'NEM', 'GOLD', 'AEM', 'KGC', 'AU', 'AGI', 'HL', 'CDE', 'PAAS',
        'AG', 'MAG', 'FSM', 'EXK', 'FCX', 'SCCO', 'TECK', 'HBM',
        'MP', 'LAC', 'SGML', 'LTHM', 'ALB', 'SQM', 'PLL', 'ALTM',
        'BHP', 'RIO', 'VALE', 'CLF', 'X', 'NUE', 'STLD', 'AA',
    ],
    '🏭 Industrial': [
        'CAT', 'DE', 'CMI', 'PCAR', 'AGCO', 'OSK', 'TEX', 'CNHI',
        'GE', 'HON', 'MMM', 'EMR', 'ROK', 'ETN', 'PH', 'ITW', 'IR',
        'UPS', 'FDX', 'XPO', 'JBHT', 'ODFL', 'CHRW', 'SAIA', 'EXPD',
        'URI', 'PWR', 'MTZ', 'FAST', 'WSO', 'GWW', 'POOL', 'SWK',
    ],
    '🛒 Retail/Consumer': [
        'WMT', 'TGT', 'COST', 'HD', 'LOW', 'DG', 'DLTR', 'FIVE', 'OLLI',
        'ULTA', 'LULU', 'NKE', 'DECK', 'CROX', 'TJX', 'ROST', 'BURL', 'GPS',
        'MCD', 'SBUX', 'CMG', 'WING', 'DPZ', 'YUM', 'QSR', 'DRI', 'TXRH',
        'PG', 'KO', 'PEP', 'MNST', 'CELH', 'KDP', 'KHC', 'GIS', 'K',
    ],
    '🏠 Real Estate': [
        'EQIX', 'DLR', 'AMT', 'CCI', 'SBAC', 'PLD', 'STAG', 'REXR',
        'O', 'SPG', 'AVB', 'EQR', 'MAA', 'INVH', 'AMH', 'SUI',
        'WELL', 'VTR', 'PEAK', 'PSA', 'EXR', 'CUBE', 'LSI',
    ],
    '📊 Sector ETFs': [
        'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLU', 'XLRE',
        'XLC', 'XME', 'XRT', 'XHB', 'XOP', 'XES', 'XPH', 'IBB', 'XBI', 'SMH',
        'SOXX', 'IGV', 'IGE', 'IYT', 'IYF', 'IYW', 'IYZ', 'IYC', 'IYH', 'IYJ',
    ],
    '📈 Mid-Cap Growth': [
        'FOUR', 'DOCN', 'BILL', 'FROG', 'ESTC', 'ASAN', 'FRSH', 'NCNO', 'APPN',
        'ALRM', 'MIME', 'QLYS', 'VRNS', 'TENB', 'RDWR', 'SPLK', 'RPD', 'EVBG',
        'ALRM', 'MIME', 'QLYS', 'VRNS', 'TENB', 'RDWR', 'SPLK', 'RPD', 'EVBG',
    ],
    '🚀 Small-Cap Growth': [
        'UPST', 'SOFI', 'AFRM', 'OPEN', 'RKT', 'UWMC', 'CLOV', 'WISH', 'SPCE',
        'RBLX', 'HOOD', 'COIN', 'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF', 'BTBT',
        'LC', 'NU', 'ADYEN', 'SQ', 'PYPL', 'V', 'MA', 'AXP', 'FIS', 'FISV',
    ],
    '🏥 Mid-Cap Healthcare': [
        'HIMS', 'CRSP', 'BEAM', 'NTLA', 'EDIT', 'VERV', 'PRME', 'LEGN', 'VKTX',
        'ALT', 'GPCR', 'SRPT', 'ALNY', 'BMRN', 'IONS', 'FOLD', 'RGNX', 'ARWR',
        'SGMO', 'BLUE', 'RARE', 'FATE', 'ALLO', 'SANA', 'KYMR', 'RPTX', 'ALKS',
    ],
    '🏭 Mid-Cap Industrial': [
        'URI', 'PWR', 'MTZ', 'FAST', 'WSO', 'GWW', 'POOL', 'SWK', 'TTC',
        'AOS', 'WWD', 'AWI', 'TREX', 'AZEK', 'CSL', 'GVA', 'ROAD', 'ASTE',
        'ATKR', 'ESE', 'FLS', 'GFF', 'HWM', 'IEX', 'ITT', 'KBR', 'LNN',
    ],
    '🛒 Mid-Cap Consumer': [
        'ULTA', 'LULU', 'DECK', 'CROX', 'TJX', 'ROST', 'BURL', 'GPS', 'ANF',
        'AEO', 'DKS', 'BBWI', 'HBI', 'LEVI', 'PVH', 'RL', 'TPX', 'WSM',
        'W', 'ETSY', 'EBAY', 'RVLV', 'REAL', 'REVG', 'REV',
    ],
}

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 🇧🇷 BRAZILIAN MARKET (B3) - COMPREHENSIVE COVERAGE                          │
# └─────────────────────────────────────────────────────────────────────────────┘

BRAZIL_SECTORS = {
    '🏦 Bancos BR': [
        'ITUB4.SA', 'BBDC4.SA', 'BBDC3.SA', 'BBAS3.SA', 'SANB11.SA', 
        'BPAC11.SA', 'ITSA4.SA', 'BRSR6.SA', 'ABCB4.SA', 'BMGB4.SA',
    ],
    '💳 Financeiras BR': [
        'B3SA3.SA', 'CIEL3.SA', 'BBSE3.SA', 'PSSA3.SA', 'SULA11.SA',
        'IRBR3.SA', 'WIZC3.SA',
    ],
    '⛽ Petróleo BR': [
        'PETR4.SA', 'PETR3.SA', 'PRIO3.SA', 'RECV3.SA', 'RRRP3.SA',
        'CSAN3.SA', 'UGPA3.SA', 'VBBR3.SA', 'DMMO3.SA',
    ],
    '⛏️ Mineração BR': [
        'VALE3.SA', 'CSNA3.SA', 'GGBR4.SA', 'USIM5.SA', 'GOAU4.SA',
        'CMIN3.SA', 'CBAV3.SA', 'BRAP4.SA',
    ],
    '📄 Papel/Celulose BR': [
        'SUZB3.SA', 'KLBN11.SA', 'KLBN4.SA', 'RANI3.SA', 'DXCO3.SA',
    ],
    '🛒 Varejo BR': [
        'MGLU3.SA', 'LREN3.SA', 'ARZZ3.SA', 'SOMA3.SA', 'GRND3.SA',
        'RADL3.SA', 'PNVL3.SA', 'CRFB3.SA', 'ASAI3.SA', 'PCAR3.SA',
        'GMAT3.SA', 'VIVA3.SA', 'AMAR3.SA', 'CEAB3.SA',
    ],
    '🍖 Alimentos BR': [
        'JBSS3.SA', 'BRFS3.SA', 'MRFG3.SA', 'BEEF3.SA', 'MDIA3.SA',
        'ABEV3.SA', 'SMTO3.SA', 'CAML3.SA', 'SLCE3.SA',
    ],
    '⚡ Energia BR': [
        'ELET3.SA', 'ELET6.SA', 'CPFE3.SA', 'CMIG4.SA', 'EQTL3.SA',
        'TAEE11.SA', 'EGIE3.SA', 'ENGI11.SA', 'NEOE3.SA', 'AURE3.SA',
        'CPLE6.SA', 'AESB3.SA', 'TRPL4.SA', 'MEGA3.SA',
    ],
    '💧 Saneamento BR': [
        'SBSP3.SA', 'SAPR11.SA', 'CSMG3.SA', 'ORVR3.SA',
    ],
    '🚗 Transporte BR': [
        'CCRO3.SA', 'ECOR3.SA', 'RAIL3.SA', 'STBP3.SA', 'HBSA3.SA',
        'AZUL4.SA', 'GOLL4.SA', 'EMBR3.SA', 'POMO4.SA',
    ],
    '🏗️ Construção BR': [
        'MRVE3.SA', 'CYRE3.SA', 'EZTC3.SA', 'DIRR3.SA', 'TEND3.SA',
        'EVEN3.SA', 'TRIS3.SA', 'PLPL3.SA', 'MDNE3.SA', 'LAVV3.SA',
    ],
    '📱 Tech/Telecom BR': [
        'WEGE3.SA', 'TOTS3.SA', 'LWSA3.SA', 'POSI3.SA', 'INTB3.SA',
        'VIVT3.SA', 'TIMS3.SA', 'OIBR3.SA', 'CASH3.SA',
    ],
    '🏥 Saúde BR': [
        'RDOR3.SA', 'HAPV3.SA', 'FLRY3.SA', 'DASA3.SA', 'MATD3.SA',
        'AALR3.SA', 'QUAL3.SA', 'ONCO3.SA', 'HYPE3.SA', 'BLAU3.SA',
    ],
    '🏭 Industrial BR': [
        'WEGE3.SA', 'EMBR3.SA', 'RAPT4.SA', 'TUPY3.SA', 'FRAS3.SA',
        'ROMI3.SA', 'KEPL3.SA', 'SHUL4.SA', 'MYPK3.SA',
    ],
    '🏦 Bancos Regionais BR': [
        'BPAN4.SA', 'SANB4.SA', 'BRSR3.SA', 'BMEB4.SA', 'BGIP4.SA',
        'BRAP4.SA', 'BRIV4.SA', 'CRIV4.SA', 'ITSA3.SA', 'ITSA4.SA',
        'BPAC11.SA', 'SANB11.SA', 'BRSR6.SA', 'BMEB4.SA', 'BGIP4.SA',
    ],
    '🛒 Varejo Regional BR': [
        'GUAR3.SA', 'LIGT3.SA', 'VVAR3.SA', 'VVAR11.SA', 'VVAR4.SA',
        'GUAR3.SA', 'LIGT3.SA', 'VVAR3.SA', 'VVAR11.SA', 'VVAR4.SA',
    ],
    '⚡ Energia Regional BR': [
        'CEPE6.SA', 'CEPE3.SA', 'CEPE5.SA', 'CEPE6.SA', 'CEPE3.SA',
        'CEPE5.SA', 'CEPE6.SA', 'CEPE3.SA', 'CEPE5.SA', 'CEPE6.SA',
    ],
    '🏗️ Construção Regional BR': [
        'JHSF3.SA', 'JHSF4.SA', 'JHSF11.SA', 'JHSF3.SA', 'JHSF4.SA',
        'JHSF11.SA', 'JHSF3.SA', 'JHSF4.SA', 'JHSF11.SA', 'JHSF3.SA',
    ],
    '📱 Tech Regional BR': [
        'LWSA3.SA', 'TOTS3.SA', 'POSI3.SA', 'INTB3.SA', 'CASH3.SA',
        'LWSA3.SA', 'TOTS3.SA', 'POSI3.SA', 'INTB3.SA', 'CASH3.SA',
    ],
}
