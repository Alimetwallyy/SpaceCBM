import streamlit as st
import pandas as pd
import io
from utils import calculate_cbm_from_df
import plotly.express as px

st.set_page_config(page_title="CBM Calculator", layout="wide")

st.title("CBM Calculator — Bin Volume Analysis (cm → m³)")

st.markdown(
    """
    Upload an Excel file with bin dimensions (in **cm**). Map the columns if they differ from default names.

    Expected units: **centimetres (cm)**. CBM calculation uses: (H * W * D) / 1,000,000.
    """
)

# Sidebar: upload and options
st.sidebar.header("Upload & Options")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file (.xlsx)", type=["xlsx", "xls", "csv"])

sample_download = st.sidebar.button("Download sample CSV template")
if sample_download:
    # provide a small CSV template in memory
    sample_df = pd.DataFrame({
        'BinID': ['B001', 'B002', 'B003'],
        'Height_cm': [10, 12, 8],
        'Width_cm': [30, 20, 25],
        'Depth_cm': [30, 30, 30],
        'Usage': ['drawer', 'non-drawer', 'drawer']
    })
    towrite = io.BytesIO()
    sample_df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.sidebar.download_button('Download CSV template', data=towrite, file_name='sample_bins_template.csv', mime='text/csv')

st.sidebar.markdown("---")
round_decimals = st.sidebar.number_input('Round CBM to decimal places', min_value=0, max_value=6, value=3)
threshold_cbm = st.sidebar.number_input('Highlight bins with CBM <= (m³)', min_value=0.0, value=0.05, step=0.01)

# Read file
if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.subheader("Data preview")
    st.dataframe(df.head())

    # Column mapping UI
    st.subheader("Column mapping")
    cols = df.columns.tolist()
    st.info("Map which columns correspond to BinID, Height, Width, Depth (units: cm). If you have an optional 'Usage' column (drawer/non-drawer), map it too.")

    col_bin = st.selectbox("Bin ID column", options=[None] + cols, index=cols.index('BinID') if 'BinID' in cols else 0)
    col_h = st.selectbox("Height column (cm)", options=cols, index=cols.index('Height') if 'Height' in cols else 0)
    col_w = st.selectbox("Width column (cm)", options=cols, index=cols.index('Width') if 'Width' in cols else 1 if len(cols)>1 else 0)
    col_d = st.selectbox("Depth column (cm)", options=cols, index=cols.index('Depth') if 'Depth' in cols else 2 if len(cols)>2 else 0)
    col_usage = st.selectbox("Optional: Usage / Type column (e.g. drawer/non-drawer)", options=[None] + cols, index=cols.index('Usage') if 'Usage' in cols else 0)

    if st.button("Calculate CBM"):
        try:
            result_df = calculate_cbm_from_df(df, col_h, col_w, col_d, col_bin, round_decimals)
        except Exception as e:
            st.error(f"Error calculating CBM: {e}")
            st.stop()

        # Merge usage column if provided
        if col_usage and col_usage in df.columns:
            result_df['Usage'] = df[col_usage].astype(str)

        # Show summary KPIs
        st.subheader("High-level summary")
        total_bins = len(result_df)
        total_cbm = result_df['CBM_m3'].sum()
        avg_cbm = result_df['CBM_m3'].mean()
        median_cbm = result_df['CBM_m3'].median()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total bins", f"{total_bins}")
        kpi2.metric("Total CBM (m³)", f"{total_cbm:.{round_decimals}f}")
        kpi3.metric("Average CBM (m³)", f"{avg_cbm:.{round_decimals}f}")
        kpi4.metric("Median CBM (m³)", f"{median_cbm:.{round_decimals}f}")

        # Highlight small bins
        small_bins = result_df[result_df['CBM_m3'] <= threshold_cbm]
        st.write(f"Bins with CBM <= {threshold_cbm} m³: {len(small_bins)}")

        # Dataframe and conditional formatting
        st.subheader('Results table')
        st.dataframe(result_df)

        # Download updated excel
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name='CBM')
            # optionally write small bins as separate sheet
            small_bins.to_excel(writer, index=False, sheet_name='Small_Bins')
        towrite.seek(0)
        st.download_button('Download results (Excel)', data=towrite, file_name='bins_with_cbm.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Charts: histogram and breakdowns
        st.subheader('Visualizations')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(result_df, x='CBM_m3', nbins=30, title='CBM distribution (m³)')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.box(result_df, y='CBM_m3', title='CBM boxplot (m³)')
            st.plotly_chart(fig2, use_container_width=True)

        # Optional breakdown by Usage
        if 'Usage' in result_df.columns:
            st.subheader('Breakdown by Usage')
            by_usage = result_df.groupby('Usage').agg(Total_CBm=('CBM_m3','sum'), Avg_CBm=('CBM_m3','mean'), Count=('BinID','count')).reset_index()
            st.dataframe(by_usage)
            fig3 = px.bar(by_usage, x='Usage', y='Total_CBm', hover_data=['Count','Avg_CBm'], title='Total CBM by Usage')
            st.plotly_chart(fig3, use_container_width=True)

        st.success('Calculation complete.')

else:
    st.info('Upload an Excel/CSV file to begin. Use the sidebar to download a sample CSV template.')
