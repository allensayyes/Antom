import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 修复sklearn导入问题
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
except ImportError:
    st.error("⚠️ 缺少 scikit-learn 库，请运行: pip install scikit-learn")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="Antom BI Analytics Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .data-source {
        font-size: 0.8rem;
        color: #7f8c8d;
        font-style: italic;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">🏦 Antom 跨境收单业务智能分析平台Demo</h1>', unsafe_allow_html=True)

# 侧边栏
st.sidebar.title("📊 分析维度")
analysis_type = st.sidebar.selectbox(
    "选择分析类型",
    ["业务概览", "交易平台渗透", "行业规模分析"]
)

# 数据源信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 数据来源")
st.sidebar.markdown("""
- **[Antom官方数据](https://www.antom.com/cn/about-us/)**: 业务报告、交易数据
- **[行业报告](https://www.mckinsey.com/industries/financial-services/our-insights)**: Statista、麦肯锡、普华永道
- **[公开数据](https://www.pwc.com/gx/en/industries/financial-services.html)**: 央行、金融监管机构
- **第三方数据**: 支付行业研究报告
- **虚构数据**: 根据公开信息和行业报告虚构的数据
""")

# 模拟真实数据（基于公开信息）
@st.cache_data
def load_antom_data():
    """加载Antom相关数据"""
    
    # 全球业务概览数据（2025年上半年，示例）
    global_overview = {
        'total_merchants': 125000000,  # 1.25亿商户
        'total_consumers': 1850000000,  # 18.5亿消费者
        'countries_covered': 50,  # 50+国家
        'platforms_covered': 12,  # 覆盖平台数量（示例）
        'monthly_transactions': 2800000000,  # 月交易量（示例）
        'total_volume_2025H1': 780000000000  # 2025年上半年总交易额（美元）
    }
    
    # 地区市场数据（2025 H1，示例）
    regional_data = pd.DataFrame({
        'region': ['亚太', '欧洲', '北美', '拉美', '中东非洲', '其他'],
        'merchants_millions': [50, 27, 22, 17, 12, 6],
        'consumers_millions': [860, 420, 320, 230, 120, 55],
        'transaction_volume_billions': [650, 320, 270, 170, 115, 60],
        'growth_rate': [14.5, 11.2, 7.9, 20.8, 17.1, 9.4]
    })
    
    # 国家级别的数据（用于地图可视化，含增长率）
    country_data = pd.DataFrame({
        'iso_alpha': ['CHN', 'USA', 'JPN', 'GBR', 'DEU', 'FRA', 'IND', 'SGP', 'THA', 'IDN', 
                      'MYS', 'PHL', 'VNM', 'KOR', 'AUS', 'BRA', 'MEX', 'ARE', 'ZAF', 'CAN'],
        'country': ['中国', '美国', '日本', '英国', '德国', '法国', '印度', '新加坡', '泰国', '印尼',
                    '马来西亚', '菲律宾', '越南', '韩国', '澳大利亚', '巴西', '墨西哥', '阿联酋', '南非', '加拿大'],
        'transaction_volume_billions': [620, 315, 255, 205, 185, 155, 370, 105, 155, 210,
                                    185, 125, 105, 185, 125, 160, 130, 105, 95, 115],
        'growth_rate': [12.5, 8.2, 6.1, 7.0, 6.5, 6.0, 14.8, 9.3, 10.1, 11.2, 9.4, 8.7, 9.9, 7.5, 6.8, 13.1, 12.0, 10.5, 9.6, 7.9],
        'region': ['亚太', '北美', '亚太', '欧洲', '欧洲', '欧洲', '亚太', '亚太', '亚太', '亚太',
                   '亚太', '亚太', '亚太', '亚太', '亚太', '拉美', '拉美', '中东非洲', '中东非洲', '北美']
    })
    
    # 支付方式数据（2025 H1，示例）
    payment_methods = pd.DataFrame({
        'method': ['银行卡', '电子钱包', '网银转账', '数字银行', 'BNPL', '加密货币', '其他'],
        'usage_percentage': [34.1, 30.2, 17.6, 9.5, 5.4, 1.9, 1.3],
        'transaction_volume': [455, 385, 235, 118, 65, 25, 17],
        'growth_rate': [7.9, 22.6, 4.8, 38.2, 95.4, 9.6, 2.0]
    })
    
    # 商户行业分布
    merchant_industries = pd.DataFrame({
        'industry': ['电商零售', '餐饮酒店', '旅游出行', '金融服务', '教育培训', '医疗健康', '游戏娱乐', '其他'],
        'merchant_count': [25000000, 18000000, 15000000, 12000000, 8000000, 7000000, 5000000, 10000000],
        'avg_transaction': [85, 45, 120, 200, 35, 90, 25, 60],
        'monthly_volume': [2125000000, 810000000, 1800000000, 2400000000, 280000000, 630000000, 125000000, 600000000]
    })

    # 平台覆盖与渗透（示例）
    platform_penetration = pd.DataFrame({
        'platform': ['AliExpress', 'Lazada', 'TikTok Shop', 'Temu', 'Shopee', 'Amazon Global', 'Daraz', 'Trendyol', 'Noon', 'MercadoLibre', 'Flipkart', 'eBay Global'],
        'region': ['全球', '东南亚', '全球', '全球', '东南亚', '全球', '南亚', '欧洲/中东', '中东', '拉美', '印度', '全球'],
        'onboard_date': ['2015-03', '2016-07', '2022-05', '2023-09', '2017-01', '2019-04', '2018-06', '2020-02', '2019-11', '2017-08', '2019-03', '2018-01'],
        'merchants_m': [12.0, 8.5, 6.2, 3.8, 7.1, 9.0, 1.8, 2.2, 1.1, 4.5, 3.0, 4.0],
        'users_m': [320.0, 210.0, 180.0, 150.0, 190.0, 260.0, 40.0, 55.0, 35.0, 220.0, 150.0, 200.0],
        # GMV（十亿美元），按你提供的2024榜单口径覆盖（未列出平台保留现值）
        'gmv_b': [30.0, 15.0, 15.0, 20.0, 40.7, 350.0, 1.2, 16.0, 3.5, 24.0, 25.0, 37.0],
        'compliance_risk': ['低', '中', '中', '中', '中', '低', '中', '中', '中', '中高', '中', '低']
    })

    # 竞对分析（示例）
    competitor_data = pd.DataFrame({
        'region': ['亚太', '欧洲', '北美', '拉美', '中东非', '全球'],
        'platform': ['Shopee/Lazada', 'Amazon/EU PSPs', 'Stripe/Adyen', 'MercadoPago', 'Noon/Local PSPs', 'TikTok Shop/Temu'],
        'main_competitors': ['Stripe, Adyen, Xendit', 'Adyen, Worldline, Checkout.com', 'Stripe, Adyen, PayPal Braintree', 'dLocal, EBANX', 'Checkout.com, Tap, HyperPay', 'Stripe, Adyen, PayPal'],
        'antom_strength': ['本地钱包覆盖深、费率优势', '多币种结算与风控联动', '大促稳定性与风控', '本地化钱包/分期', '监管沟通与本地方案', '平台深度合作与路由优化'],
        'antom_gap': ['中小商户触达', '部分国家合规牌照', '长尾行业拓展', '清结算时效', '风控数据本地化', '个别支付方式深度']
    })
    
    # 时间序列数据（截至2025年6月）
    np.random.seed(42)  # 固定随机种子，确保数据一致性
    dates = pd.date_range(start='2023-01-01', end='2025-06-30', freq='M')
    
    # 创建更真实的趋势数据
    base_volume = 1000
    growth_trend = np.linspace(0, 0.42, len(dates))
    seasonal = 0.1 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
    noise = np.random.normal(0, 0.05, len(dates))
    transaction_volume = base_volume * (1 + growth_trend + seasonal + noise)
    
    time_series_data = pd.DataFrame({
        'date': dates,
        'transaction_volume': transaction_volume,
        'merchant_count': 50 + np.linspace(0, 20, len(dates)) + np.random.normal(0, 2, len(dates)),
        'fraud_rate': 0.15 + np.linspace(0, -0.05, len(dates)) + np.random.normal(0, 0.01, len(dates)),
        'customer_satisfaction': 4.2 + np.linspace(0, 0.2, len(dates)) + np.random.normal(0, 0.05, len(dates))
    })
    
    return global_overview, regional_data, payment_methods, merchant_industries, time_series_data, country_data, platform_penetration, competitor_data

# 加载数据
global_overview, regional_data, payment_methods, merchant_industries, time_series_data, country_data, platform_penetration, competitor_data = load_antom_data()

# 根据选择的分析类型显示不同内容
if analysis_type == "业务概览":
    st.markdown('<div class="section-header">🌍 To B跨境收单业务概览</div>', unsafe_allow_html=True)
    # st.info("💡 **Antom定位**: Antom是蚂蚁国际专门为阿里国际出海电商（如AliExpress、Lazada等）商家提供的To B跨境收单服务平台。在Antom推出前，商家需要对接多个支付服务商；现在可通过Antom一站式接入300+支付方式，覆盖200+国家。")
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌐 覆盖国家",
            value=f"{int(global_overview['countries_covered'])}+",
            delta="新增15个国家"
        )
    
    with col2:
        st.metric(
            label="🏪 商户数量",
            value=f"{global_overview['total_merchants']/1_000_000:.1f}M",
            delta="+12.5%"
        )
    
    with col3:
        st.metric(
            label="👥 消费者",
            value=f"{global_overview['total_consumers']/1_000_000:.1f}M",
            delta="+8.3%"
        )
    
    with col4:
        st.metric(
            label="🧭 渗透平台",
            value=f"{global_overview['platforms_covered']}+",
            delta="新增2个平台"
        )
    
    # 全球业务分布地图（上下排列：交易量在上，增长率在下）
    st.markdown("### 🗺️ 全球业务分布")
    fig_vol = px.choropleth(
        country_data,
        locations="iso_alpha",
        color="transaction_volume_billions",
        hover_name="country",
        hover_data={
            "region": True,
            "transaction_volume_billions": ":,.0f",
            "growth_rate": ":.1f"
        },
        title="交易量分布（十亿美元）",
        color_continuous_scale="Blues",
        projection="natural earth"
    )
    fig_vol.update_layout(
        height=620,
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    # 移除所有自定义标注
    st.plotly_chart(fig_vol, use_container_width=True)

    fig_g = px.choropleth(
        country_data,
        locations="iso_alpha",
        color="growth_rate",
        hover_name="country",
        hover_data={
            "region": True,
            "transaction_volume_billions": ":,.0f",
            "growth_rate": ":.1f"
        },
        title="增长率分布（%）",
        color_continuous_scale="RdYlGn",
        projection="natural earth"
    )
    fig_g.update_layout(
        height=620,
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown('<div class="data-source">数据来源: <a href="https://www.antom.com/cn/about-us/" target="_blank">Antom官方业务报告</a>, 2025年H1</div>', unsafe_allow_html=True)

elif analysis_type == "交易平台渗透":
    st.markdown('<div class="section-header">🧭 交易平台渗透与对比</div>', unsafe_allow_html=True)
    st.info("当前Antom已覆盖主要全球与区域电商/内容电商平台，以下展示各平台渗透率, 竞对分析以及发展建议。")
    with st.container():
        # 构造各平台收单渗透率（示例数据，三类之和=100%）
        share_df = pd.DataFrame({
            'platform': platform_penetration['platform'],
        # 提升 AliExpress（索引0）中 Antom 占比至 0.80
            'Antom': [0.80, 0.52, 0.35, 0.28, 0.40, 0.22, 0.30, 0.26, 0.25, 0.18, 0.24, 0.20],
        # 相应下调 AliExpress 的主要竞对份额，保证总和<=1（Others 自动计算）
            '主要竞对': [0.15, 0.34, 0.50, 0.60, 0.45, 0.65, 0.55, 0.58, 0.62, 0.70, 0.60, 0.68]
        })
        share_df['Others'] = 1 - share_df['Antom'] - share_df['主要竞对']
        # 调整阿里国际旗下平台（AliExpress, Lazada, Trendyol, Daraz）中 Antom 占比至 ~60%
        ali_intl_platforms = ['AliExpress', 'Lazada', 'Trendyol', 'Daraz']
        for p in ali_intl_platforms:
            if p in share_df['platform'].values:
                idx = share_df.index[share_df['platform'] == p][0]
                orig_comp = float(share_df.loc[idx, '主要竞对'])
                orig_oth = float(share_df.loc[idx, 'Others'])
                rest = max(orig_comp + orig_oth, 1e-6)
                new_antom = 0.60
                rem = 1.0 - new_antom
                share_df.loc[idx, 'Antom'] = new_antom
                share_df.loc[idx, '主要竞对'] = rem * (orig_comp / rest)
                share_df.loc[idx, 'Others'] = rem * (orig_oth / rest)
        # 调整 Amazon Global 的渗透结构：Amazon Pay 90%，Antom 8%，Others 2%
        if 'Amazon Global' in share_df['platform'].values:
            _idx = share_df.index[share_df['platform'] == 'Amazon Global'][0]
            share_df.loc[_idx, '主要竞对'] = 0.90
            share_df.loc[_idx, 'Antom'] = 0.08
            share_df.loc[_idx, 'Others'] = 1 - share_df.loc[_idx, 'Antom'] - share_df.loc[_idx, '主要竞对']
        # 平台总GMV与入驻时间（十亿美元）
        meta_cols = platform_penetration[['platform', 'gmv_b', 'onboard_date']].drop_duplicates()
        plot_df = share_df.merge(meta_cols, on='platform', how='left')

        # 按交易额堆叠柱状图：
        # - x轴按GMV降序排序
        # - y轴使用实际GMV（十亿美元）
        # 计算排序
        plot_df = plot_df.sort_values('gmv_b', ascending=False).reset_index(drop=True)

        # 上下子图：上为堆叠柱，下为入驻时间轴
        fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                             row_heights=[0.82, 0.18], subplot_titles=(None, None))
        for name, color in zip(['Antom', '主要竞对', 'Others'], ['#2E86DE', '#E67E22', '#95A5A6']):
            actual_amount = plot_df[name] * plot_df['gmv_b']
            segment_share = plot_df[name]
            custom = np.column_stack((actual_amount, segment_share, plot_df['gmv_b']))
            fig1.add_trace(go.Bar(
                x=plot_df['platform'],
                y=actual_amount,
                name=name,
                marker_color=color,
                customdata=custom,
                hovertemplate=(
                    f"%{{x}}<br>{name}: $%{{customdata[0]:.1f}}B"
                    f"<br>渗透率: %{{customdata[1]:.1%}}"
                    f"<br>平台总GMV: $%{{customdata[2]:.1f}}B<extra></extra>"
                )
            ), row=1, col=1)

        # 下方入驻时间轴（与柱子对齐）
        fig1.add_trace(
            go.Scatter(
                x=plot_df['platform'],
                y=[0] * len(plot_df),
                mode='markers+text',
                marker=dict(color='#34495E', size=8),
                text=plot_df['onboard_date'],
                textposition='top center',
                hoverinfo='skip',
                showlegend=False
            ), row=2, col=1
        )
        # 时间轴样式
        fig1.update_yaxes(visible=False, row=2, col=1)
        fig1.add_hline(y=0, line_width=1, line_color='#95A5A6', row=2, col=1)
        fig1.update_layout(
            barmode='stack',
            title='各平台渗透结构与总交易额（按交易额堆叠）',
            height=560,
            xaxis_tickangle=-30,
            yaxis_title='总交易额（十亿美元）',
            legend_title_text='收单服务商',
            xaxis=dict(categoryorder='array', categoryarray=plot_df['platform'].tolist())
        )
        # 在主要竞对分段中部标注单一品牌（加粗）
        top_competitor = {
            'AliExpress': 'Stripe',
            'Lazada': 'Adyen',
            'TikTok Shop': 'Stripe',
            'Temu': 'Adyen',
            'Shopee': 'Xendit',
            'Amazon Global': 'Amazon Pay',
            'Daraz': '2C2P',
            'Trendyol': 'iyzico',
            'Noon': 'Checkout.com',
            'MercadoLibre': 'dLocal',
            'Flipkart': 'Razorpay',
            'eBay Global': 'PayPal'
        }
        for i, row in plot_df.iterrows():
            antom_disp = row['Antom'] * row['gmv_b']
            comp_disp = row['主要竞对'] * row['gmv_b']
            label = top_competitor.get(row['platform'], '主要竞对')
            fig1.add_annotation(
                x=row['platform'],
                y=antom_disp + comp_disp / 2,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=12, color='white'),
                align='center'
            )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('<div class="data-source">GMV为行业估算中位值（单位：十亿美元）；来源综合财报/招股书、权威媒体与机构数据库（区间口径略有差异，仅用于可视化演示）。数据时间：截至2024年全年，更新于2025-01。渗透率为演示用数据，非官方披露，仅用于面试展示。</div>', unsafe_allow_html=True)
    # 竞对对照（融合表格）
    st.markdown("### 🧭 竞对对照与渗透建议")
    suggestions_map = {
        'Shopee/Lazada': '阿里系/东南亚：本地钱包与分期联动；新客90天加速包；内容电商失败重试+智能路由',
        'Amazon/EU PSPs': '全球：切入长尾跨境卖家，多币种结算与稳定性；站外支付联名营销',
        'Stripe/Adyen': '全球独立站：差异化费控+更优路由；联动风控阈值灰度提升转化',
        'MercadoPago': '拉美：PIX/BOLETO/分期全量覆盖；税费字段与报关映射优化，缩短结算时延',
        'Noon/Local PSPs': '中东：对接Tap/HyperPay补齐方式；伊斯兰金融合规与数据本地化优先',
        'TikTok Shop/Temu': '内容/低客单：小额授权与批量对账优化；风控阈值AB，保转化与安全'
    }
    competitor_display = competitor_data.copy()
    competitor_display['渗透建议'] = competitor_display['platform'].map(suggestions_map).fillna('按区域定制：方式矩阵+结算效率+风控转化三要素联动')
    competitor_display = competitor_display.rename(columns={
        'region': '区域',
        'platform': '平台/场景',
        'main_competitors': '主要竞对',
        'antom_strength': 'Antom优势',
        'antom_gap': 'Antom差距'
    })
    st.dataframe(competitor_display, use_container_width=True)
    st.markdown('<div class="data-source">数据来源: 行业公开信息与平台观察（示例），2025年H1</div>', unsafe_allow_html=True)

elif analysis_type == "竞对分析":
    # 已移除：竞对分析模块合并至“交易平台渗透”
    pass

elif analysis_type == "支付成功率分析":
    st.markdown('<div class="section-header">💳 跨境收单支付成功率分析</div>', unsafe_allow_html=True)
    
    # 添加说明
    st.info("📊 **To B收单场景**: 以下数据展示的是**Antom为阿里国际商家提供的跨境收单**支付成功率和各支付方式的使用情况。对于To B业务，支付成功率直接影响商家的GMV转化。")
    
    # BNPL解释
    with st.expander("❓ 什么是BNPL？"):
        st.markdown("""
        **BNPL (Buy Now, Pay Later - 先买后付)** 是一种新兴的支付方式：
        - 允许消费者购买商品或服务时先享受，后付款
        - 通常将总金额分成几期免息支付
        - 深受年轻消费者欢迎，特别适用于电商和零售场景
        - 是目前增长最快的支付方式之一
        """)
    
    # 支付方式使用分布
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(
            payment_methods,
            values='usage_percentage',
            names='method',
            title='支付方式使用分布',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(
            payment_methods,
            x='method',
            y='growth_rate',
            title='各支付方式增长率（%）',
            color='growth_rate',
            color_continuous_scale='RdYlGn'
        )
        fig2.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 支付方式趋势分析
    st.markdown("### 📈 支付方式发展趋势")
    
    # 模拟时间序列数据
    np.random.seed(42)  # 固定随机种子
    months = pd.date_range('2023-01-01', '2024-12-31', freq='M')
    payment_trends = pd.DataFrame({
        'date': months,
        '银行卡': np.random.normal(35, 2, len(months)),
        '电子钱包': np.random.normal(28, 3, len(months)) + np.linspace(0, 5, len(months)),
        '网银转账': np.random.normal(18, 1, len(months)),
        '数字银行': np.random.normal(8, 1, len(months)) + np.linspace(0, 3, len(months)),
        'BNPL': np.random.normal(4, 0.5, len(months)) + np.linspace(0, 2, len(months))
    })
    
    fig3 = px.line(
        payment_trends,
        x='date',
        y=['银行卡', '电子钱包', '网银转账', '数字银行', 'BNPL'],
        title='支付方式使用趋势（2023-2024）',
        labels={'value': '使用率（%）', 'date': '时间'}
    )
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # 成功率Shapley归因（简化演示）
    st.markdown("### 🧮 成功率归因：Shapley示例（模拟数据）")
    st.caption("目标：将整体成功率提升归因到各环节（风控预审、3DS、发卡行授权、网络连通、反洗洗钱）")
    stages = ['风控预审', '3DS验证', '发卡行授权', '网络连通', '反洗洗钱']
    baseline = 0.960
    marginal_improvements = {'风控预审': 0.005, '3DS验证': 0.004, '发卡行授权': 0.006, '网络连通': 0.003, '反洗洗钱': 0.002}
    total_gain = sum(marginal_improvements.values())
    shap_df = pd.DataFrame({'环节': list(marginal_improvements.keys()), '贡献(百分点)': [round(v*100, 2) for v in marginal_improvements.values()]})
    fig4 = px.bar(shap_df, x='环节', y='贡献(百分点)', title='Shapley 归因贡献（百分点）', color='环节')
    fig4.update_layout(height=420)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(f"整体成功率：{(baseline + total_gain)*100:.2f}%（基线{baseline*100:.2f}% + 提升{total_gain*100:.2f}%）")
    st.markdown('<div class="data-source">数据来源: <a href="https://www.antom.com/cn/about-us/" target="_blank">Antom交易数据</a>（示例），2025年H1</div>', unsafe_allow_html=True)

elif analysis_type == "行业规模分析":
    st.markdown('<div class="section-header">🏪 行业规模分析</div>', unsafe_allow_html=True)
    
    # 仅保留：商户数量 vs 平均交易金额（气泡大小=月交易量）
    fig2 = px.scatter(
        merchant_industries,
        x='merchant_count',
        y='avg_transaction',
        size='monthly_volume',
        color='industry',
        title='商户数量 vs 平均交易金额',
        labels={'merchant_count': '商户数量', 'avg_transaction': '平均交易金额（美元）'}
    )
    fig2.update_layout(height=420)
    st.plotly_chart(fig2, use_container_width=True)

    # 新增：行业强项·热力图（0-10，报告+演示补齐）
    # 去掉“其他”，并概括为6个行业
    covered_industries = [i for i in merchant_industries['industry'].tolist() if i != '其他']
    potential_industries = ['体育用品', '家具家居', '汽车后市场', '宠物用品', '母婴用品']
    industries_pool = covered_industries + [i for i in potential_industries if i not in covered_industries]
    # 精选六个行业用于对比
    industries_all = ['电商零售', '餐饮酒店', '旅游出行', '金融服务', '教育培训', '医疗健康']
    providers = ['Antom', '主要竞对', '本地PSP', '银行转账网关']

    # 生成评分矩阵：已覆盖行业 Antom 高（7-9），潜力行业 Antom 中低（3-6）；其他提供方相对分布
    np.random.seed(42)
    scores = []
    for prov in providers:
        row = []
        for ind in industries_all:
            base = 0
            if prov == 'Antom':
                base = 8 if ind in covered_industries else 4.5
            elif prov == '主要竞对':
                base = 6.5 if ind in covered_industries else 6.0
            elif prov == '本地PSP':
                base = 7.0 if ind in ['餐饮酒店','本地生活','教育培训','医疗健康','游戏娱乐'] else 5.5
            else:  # 银行转账网关
                base = 5.0
            noise = np.random.uniform(-0.6, 0.6)
            row.append(max(0, min(10, round(base + noise, 1))))
        scores.append(row)

    # 删除“行业强项·热力图”模块（按需求）

    # 行业×区域×服务商：并列热力图（y轴为服务商，含Antom）
    st.markdown("### 🧭 行业×区域×服务商：并列热力图（0-10）")
    regions = ['亚太', '欧洲', '北美', '拉美', '中东非洲']
    providers4 = ['Antom', 'Stripe', 'Adyen', '本地PSP']
    industries_all = industries_all  # 复用上文行业顺序

    # 区域偏置，保证区分度
    def region_bias(r: str) -> float:
        return {
            '亚太': 0.5,
            '欧洲': 0.2,
            '北美': 0.3,
            '拉美': 0.1,
            '中东非洲': 0.0,
        }.get(r, 0.0)

    # 生成 Z: [服务商 × (行业×区域)]
    z_matrix = []
    texts = []
    x_top_level = []    # 行业
    x_second_level = [] # 区域
    # 先准备x多级分类
    for ind in industries_all:
        for reg in regions:
            x_top_level.append(ind)
            x_second_level.append(reg)

    for prov in providers4:
        row_vals = []
        row_text = []
        for ind in industries_all:
            for reg in regions:
                if prov == 'Antom':
                    base = 8 if ind in covered_industries else 5
                elif prov == 'Stripe':
                    base = 7 if reg in ['北美', '欧洲'] else 5.5
                elif prov == 'Adyen':
                    base = 7.5 if reg == '欧洲' else 6.0
                else:  # 本地PSP
                    base = 7.0 if ind in ['餐饮酒店','本地生活','教育培训','医疗健康','游戏娱乐'] else 5.5
                val = max(0, min(10, round(base + region_bias(reg) + np.random.uniform(-0.5, 0.5), 1)))
                row_vals.append(val)
                row_text.append(str(val))
        z_matrix.append(row_vals)
        texts.append(row_text)

    fig_strip = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=[x_top_level, x_second_level],  # 多级分类：上层行业、下层区域
        y=providers4,
        colorscale='Peach',
        colorbar=dict(title='评分')
    ))

    # 在格子内标注分数
    fig_strip.update_traces(
        text=texts,
        texttemplate='%{text}',
        textfont=dict(size=10, color='#333')
    )

    fig_strip.update_layout(
        title='行业×区域×服务商：并列热力图（0-10）',
        height=460,
        xaxis_title='行业',
        yaxis_title='',
        margin=dict(l=0, r=0, t=60, b=10)
    )

    # X轴标签倾斜，便于阅读
    fig_strip.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_strip, use_container_width=True)

elif analysis_type == "风险与合规":
    st.markdown('<div class="section-header">🛡️ 风险监控与合规分析</div>', unsafe_allow_html=True)
    
    # 风险指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚨 欺诈率",
            value="0.15%",
            delta="-0.02%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="✅ 交易成功率",
            value="99.2%",
            delta="+0.3%"
        )
    
    with col3:
        st.metric(
            label="⚡ 平均响应时间",
            value="1.2s",
            delta="-0.3s",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="🔒 安全评分",
            value="98.5",
            delta="+1.2"
        )
    
    # 风险趋势图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('欺诈率趋势', '交易成功率', '响应时间', '安全事件'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 欺诈率趋势
    fig.add_trace(
        go.Scatter(x=time_series_data['date'], y=time_series_data['fraud_rate'], 
                  name='欺诈率', line=dict(color='red')),
        row=1, col=1
    )
    
    # 交易成功率
    success_rate = 100 - time_series_data['fraud_rate'] * 100
    fig.add_trace(
        go.Scatter(x=time_series_data['date'], y=success_rate, 
                  name='成功率', line=dict(color='green')),
        row=1, col=2
    )
    
    # 响应时间
    np.random.seed(42)  # 固定随机种子
    response_time = np.random.normal(1.2, 0.1, len(time_series_data))
    fig.add_trace(
        go.Scatter(x=time_series_data['date'], y=response_time, 
                  name='响应时间', line=dict(color='blue')),
        row=2, col=1
    )
    
    # 安全事件
    security_events = np.random.poisson(5, len(time_series_data))
    fig.add_trace(
        go.Scatter(x=time_series_data['date'], y=security_events, 
                  name='安全事件', line=dict(color='orange')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="data-source">数据来源: <a href="https://www.antom.com/cn/about-us/" target="_blank">Antom风控系统</a>, 2023-2025H1; 安全监控报告（示例）</div>', unsafe_allow_html=True)

elif analysis_type == "业务预测":
    st.markdown('<div class="section-header">🔮 业务预测与趋势分析</div>', unsafe_allow_html=True)
    
    # 预测模型结果
    st.markdown("### 📊 2025年业务预测")
    
    # 模拟预测数据（基于2025H2-2026H1）
    future_dates = pd.date_range('2025-07-01', '2026-06-30', freq='M')
    historical_data = time_series_data[['date', 'transaction_volume']].copy()
    
    # 简单的线性趋势预测
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    
    # 准备历史数据
    X = np.arange(len(historical_data)).reshape(-1, 1)
    y = historical_data['transaction_volume'].values
    
    # 多项式特征
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    
    # 训练模型
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # 预测未来12个月
    future_X = np.arange(len(historical_data), len(historical_data) + 12).reshape(-1, 1)
    future_X_poly = poly_features.transform(future_X)
    predictions = model.predict(future_X_poly)
    
    # 创建预测图表
    fig = go.Figure()
    
    # 历史数据
    fig.add_trace(go.Scatter(
        x=historical_data['date'],
        y=historical_data['transaction_volume'],
        mode='lines',
        name='历史数据',
        line=dict(color='blue')
    ))
    
    # 预测数据
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines',
        name='预测数据',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title='交易量预测（2023-2025）',
        xaxis_title='时间',
        yaxis_title='交易量（百万美元）',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 关键预测指标
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📈 2025年预测增长",
            value="+18.5%",
            delta="vs 2024年"
        )
    
    with col2:
        st.metric(
            label="💰 预测交易额",
            value="$1.48T",
            delta="+$230B"
        )
    
    with col3:
        st.metric(
            label="🏪 预测商户数",
            value="1.2B",
            delta="+200M"
        )
    
    st.markdown('<div class="data-source">数据来源: <a href="https://www.antom.com/cn/about-us/" target="_blank">Antom历史数据</a>, 2023-2025H1; 机器学习预测模型（示例）</div>', unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    <p>🏦 Antom BI Analytics Dashboard | 数据驱动业务决策 </p>
    <p>© 2025 蚂蚁国际 Antom 侯良语面试Demo| 数据由互联网公开信息和虚构数据组成</p>
</div>
""", unsafe_allow_html=True)
