import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# محاولة استيراد المكتبات الرسومية مع التعامل مع الأخطاء
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    st.warning("⚠️ matplotlib not available - charts will be disabled")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

try:
    from tabulate import tabulate # pyright: ignore[reportMissingModuleSource]
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="📊 Advanced Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class DataAnalyzer:
    def __init__(self):
        self.df = None
        self.df_cleaned = None
        self.numeric_columns = []
        self.categorical_columns = []
        
    def load_data(self, uploaded_file):
        """تحميل البيانات من الملف المرفوع"""
        try:
            if uploaded_file.name.endswith('.xlsx'):
                self.df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file)
            else:
                self.df = pd.read_csv(uploaded_file)
            
            self._identify_column_types()
            return True, "✅ تم تحميل البيانات بنجاح!"
        except Exception as e:
            self._create_sample_data()
            return False, f"⚠️ تم استخدام بيانات نموذجية بسبب: {str(e)}"
    
    def _create_sample_data(self):
        """إنشاء بيانات نموذجية"""
        data = {
            'Row ID': [6548, 1350, 4597, 2894, 5123, 6234, 7345, 8456, 9567, 10678],
            'Order ID': ['CA-2014-113880', 'CA-2015-141768', 'US-2017-169502', 'CA-2016-124527', 
                        'US-2018-156224', 'CA-2019-167890', 'US-2020-178901', 'CA-2021-189012', 
                        'US-2022-190123', 'CA-2023-201234'],
            'Customer Name': ['Vicky Freymann', 'Nora Pelletier', 'Matthew Grimstein', 'Chris Cornell', 
                             'Taylor Brooks', 'Sarah Johnson', 'Mike Wilson', 'Emily Davis', 
                             'David Brown', 'Lisa Miller'],
            'Segment': ['Home Office', 'Home Office', 'Home Office', 'Corporate', 'Consumer',
                       'Home Office', 'Corporate', 'Consumer', 'Home Office', 'Corporate'],
            'Region': ['Central', 'West', 'Central', 'East', 'Central', 'West', 'East', 'Central', 'West', 'East'],
            'Sales': [150.25, 200.50, 175.75, 300.20, 125.90, 250.75, 180.30, 220.45, 190.60, 275.80],
            'Profit': [5.6784, 4.8609, 5.8887, 8.9240, 12.7500, 7.3200, 6.5400, 9.8700, 5.4300, 10.2500],
            'Quantity': [3, 3, 3, 2, 1, 4, 2, 3, 2, 4],
            'Category': ['Office Supplies', 'Furniture', 'Technology', 'Office Supplies', 'Furniture',
                        'Technology', 'Office Supplies', 'Furniture', 'Technology', 'Office Supplies'],
            'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                    'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        }
        self.df = pd.DataFrame(data)
        self._identify_column_types()
    
    def _identify_column_types(self):
        """تحديد أنواع الأعمدة تلقائياً"""
        if self.df is not None:
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            self.categorical_columns = self.df.select_dtypes(include=['object']).columns.tolist()

    def explore_data(self):
        """استكشاف البيانات"""
        if self.df is None:
            return "❌ No data loaded yet!"
        
        result = []
        result.append("📊 DATA EXPLORATION")
        result.append("=" * 50)
        result.append(f"📐 Data Dimensions: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns")
        result.append(f"📋 Available Columns: {list(self.df.columns)}")
        result.append(f"🔢 Numeric Columns: {len(self.numeric_columns)}")
        result.append(f"📝 Categorical Columns: {len(self.categorical_columns)}")
        result.append(f"❎ Missing Values: {self.df.isnull().sum().sum()}")
        result.append(f"🔄 Duplicate Rows: {self.df.duplicated().sum()}")
        
        return "\n".join(result)
    
    def clean_data(self):
        """تنظيف البيانات"""
        if self.df is None:
            return "❌ No data loaded yet!"
        
        self.df_cleaned = self.df.copy()
        changes_log = []
        
        original_missing = self.df.isnull().sum().sum()
        original_duplicates = self.df.duplicated().sum()
        original_shape = self.df.shape
        
        # 1. Handle missing values
        changes_log.append("1. Handling Missing Values:")
        for col in self.df_cleaned.columns:
            if self.df_cleaned[col].isnull().sum() > 0:
                missing_count = self.df_cleaned[col].isnull().sum()
                
                if self.df_cleaned[col].dtype in ['float64', 'int64']:
                    fill_value = self.df_cleaned[col].median()
                    self.df_cleaned[col].fillna(fill_value, inplace=True)
                    changes_log.append(f"   - {col}: Filled {missing_count} values with median ({fill_value:.2f})")
                else:
                    self.df_cleaned[col].fillna('Unknown', inplace=True)
                    changes_log.append(f"   - {col}: Filled {missing_count} values with 'Unknown'")
        
        # 2. Remove duplicates
        duplicates = self.df_cleaned.duplicated().sum()
        if duplicates > 0:
            self.df_cleaned.drop_duplicates(inplace=True)
            changes_log.append(f"2. Removed {duplicates} duplicate rows")
        
        # 3. Clean text data
        changes_log.append("3. Cleaning Text Data:")
        for col in self.df_cleaned.select_dtypes(include=['object']).columns:
            self.df_cleaned[col] = self.df_cleaned[col].astype(str).str.strip()
            changes_log.append(f"   - Cleaned text column: '{col}'")
        
        self._identify_column_types()
        
        # Summary of changes
        new_missing = self.df_cleaned.isnull().sum().sum()
        new_duplicates = self.df_cleaned.duplicated().sum()
        new_shape = self.df_cleaned.shape
        
        changes_log.append("\n📊 SUMMARY OF CHANGES:")
        changes_log.append(f"   - Missing values: {original_missing} → {new_missing}")
        changes_log.append(f"   - Duplicate rows: {original_duplicates} → {new_duplicates}")
        changes_log.append(f"   - Data shape: {original_shape} → {new_shape}")
        
        return "\n".join(changes_log)
    
    def analyze_data(self):
        """تحليل البيانات"""
        if self.df_cleaned is None:
            return "❌ Please clean the data first!"
        
        result = []
        result.append("📈 DATA ANALYSIS")
        result.append("=" * 50)
        
        if len(self.numeric_columns) > 0:
            result.append("📊 Numeric Columns Analysis:")
            for col in self.numeric_columns:
                result.append(f"\n📌 {col}:")
                result.append(f"   Mean: {self.df_cleaned[col].mean():.2f}")
                result.append(f"   Median: {self.df_cleaned[col].median():.2f}")
                result.append(f"   Std Dev: {self.df_cleaned[col].std():.2f}")
                result.append(f"   Min: {self.df_cleaned[col].min():.2f}")
                result.append(f"   Max: {self.df_cleaned[col].max():.2f}")
        
        return "\n".join(result)

    def advanced_analysis(self):
        """تحليل متقدم"""
        if self.df_cleaned is None:
            return "❌ Please clean the data first!"
        
        result = []
        result.append("🔍 ADVANCED DATA ANALYSIS")
        result.append("=" * 50)
        
        # تحليل القيم المكررة
        result.append("\n📊 MOST FREQUENT VALUES ANALYSIS:")
        
        for col in self.df_cleaned.columns:
            result.append(f"\n📌 Column: {col}")
            
            value_counts = self.df_cleaned[col].value_counts().head(5)
            if len(value_counts) > 0:
                result.append(f"   Top values:")
                for value, count in value_counts.items():
                    percentage = (count / len(self.df_cleaned)) * 100
                    result.append(f"     {value}: {count} times ({percentage:.1f}%)")
        
        return "\n".join(result)
    
    def sort_data(self, column, ascending=True):
        """ترتيب البيانات"""
        if self.df_cleaned is None:
            return None, "❌ Please clean the data first!"
        
        if column not in self.df_cleaned.columns:
            return None, f"❌ Column '{column}' not found!"
        
        try:
            sorted_data = self.df_cleaned.sort_values(by=column, ascending=ascending)
            direction = "ascending" if ascending else "descending"
            return sorted_data, f"✅ Data sorted by '{column}' ({direction})"
        except Exception as e:
            return None, f"❌ Error sorting data: {str(e)}"
    
    def get_column_value_counts(self, column, top_n=10):
        """الحصول على عدد التكرارات"""
        if self.df_cleaned is None:
            return None, "❌ Please clean the data first!"
        
        if column not in self.df_cleaned.columns:
            return None, f"❌ Column '{column}' not found!"
        
        try:
            value_counts = self.df_cleaned[column].value_counts().head(top_n)
            return value_counts, "✅ Value counts retrieved successfully"
        except Exception as e:
            return None, f"❌ Error getting value counts: {str(e)}"
    
    def create_chart(self, chart_type, x_column, y_column=None):
        """إنشاء رسوم بيانية"""
        if not MATPLOTLIB_AVAILABLE:
            return None, "❌ matplotlib is not available for chart creation"
            
        if self.df_cleaned is None:
            return None, "❌ Please clean the data first!"
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == 'histogram' and x_column in self.numeric_columns:
                self.df_cleaned[x_column].hist(ax=ax, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
                ax.set_title(f'Histogram of {x_column}')
                ax.set_xlabel(x_column)
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
                
            elif chart_type == 'bar' and x_column in self.categorical_columns:
                value_counts = self.df_cleaned[x_column].value_counts().head(10)
                bars = ax.bar(value_counts.index, value_counts.values, color='lightcoral', alpha=0.7)
                ax.set_title(f'Top 10 Values in {x_column}')
                ax.set_xlabel(x_column)
                ax.set_ylabel('Count')
                plt.xticks(rotation=45)
                ax.grid(True, alpha=0.3)
                
            elif chart_type == 'scatter' and x_column in self.numeric_columns and y_column in self.numeric_columns:
                ax.scatter(self.df_cleaned[x_column], self.df_cleaned[y_column], alpha=0.6, color='green')
                ax.set_title(f'{y_column} vs {x_column}')
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.grid(True, alpha=0.3)
                
            elif chart_type == 'line' and x_column in self.numeric_columns and y_column in self.numeric_columns:
                sorted_df = self.df_cleaned.sort_values(x_column)
                ax.plot(sorted_df[x_column], sorted_df[y_column], linewidth=2, color='purple')
                ax.set_title(f'{y_column} over {x_column}')
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.grid(True, alpha=0.3)
                
            elif chart_type == 'box' and x_column in self.numeric_columns:
                ax.boxplot(self.df_cleaned[x_column].dropna())
                ax.set_title(f'Box Plot of {x_column}')
                ax.set_ylabel(x_column)
                ax.grid(True, alpha=0.3)
            
            elif chart_type == 'pie' and x_column in self.categorical_columns:
                value_counts = self.df_cleaned[x_column].value_counts().head(6)
                ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
                ax.set_title(f'Distribution of {x_column}')
            
            else:
                return None, "❌ Invalid chart type or column selection"
            
            plt.tight_layout()
            return fig, "✅ Chart created successfully!"
            
        except Exception as e:
            return None, f"❌ Error creating chart: {str(e)}"
    
    def create_correlation_matrix(self, numeric_df):
        """إنشاء مصفوفة الارتباط مع التعامل مع seaborn إذا كان غير متوفر"""
        if not MATPLOTLIB_AVAILABLE:
            return None, "❌ matplotlib is not available"
        
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            if SEABORN_AVAILABLE:
                # استخدام seaborn إذا كان متوفر
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax, fmt='.2f')
                ax.set_title('Correlation Matrix (using Seaborn)')
            else:
                # استخدام matplotlib فقط إذا seaborn غير متوفر
                corr_matrix = numeric_df.corr()
                im = ax.imshow(corr_matrix.values, cmap='coolwarm', aspect='auto')
                
                # إعداد المحاور
                ax.set_xticks(range(len(corr_matrix.columns)))
                ax.set_yticks(range(len(corr_matrix.columns)))
                ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
                ax.set_yticklabels(corr_matrix.columns)
                
                # إضافة القيم على المصفوفة
                for i in range(len(corr_matrix.columns)):
                    for j in range(len(corr_matrix.columns)):
                        text_color = 'white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black'
                        ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                               ha='center', va='center', color=text_color, fontweight='bold')
                
                # إضافة colorbar
                plt.colorbar(im, ax=ax)
                ax.set_title('Correlation Matrix (using Matplotlib)')
            
            plt.tight_layout()
            return fig, "✅ Correlation matrix created successfully!"
            
        except Exception as e:
            return None, f"❌ Error creating correlation matrix: {str(e)}"
    
    def display_organized_data(self, num_rows=10):
        """عرض البيانات بشكل منظم"""
        if self.df_cleaned is None:
            return "❌ Please clean the data first!"
        
        return self.df_cleaned.head(num_rows)

def main():
    st.markdown('<div class="main-header">📊 Advanced Data Analyzer</div>', unsafe_allow_html=True)
    
    # تحذير إذا المكتبات مش متوفرة
    if not MATPLOTLIB_AVAILABLE:
        st.warning("""
        ⚠️ **ملاحظة مهمة:** 
        - مكتبة matplotlib غير مثبتة، الرسوم البيانية لن تعمل
        - تأكد من تثبيت المكتبات المطلوبة في ملف requirements.txt
        """)
    
    if not SEABORN_AVAILABLE and MATPLOTLIB_AVAILABLE:
        st.info("📊 seaborn غير مثبت، سيتم استخدام matplotlib للرسوم البيانية")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DataAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose your data file",
            type=['csv', 'xlsx'],
            help="Upload CSV or Excel files"
        )
        
        if uploaded_file is not None:
            success, message = analyzer.load_data(uploaded_file)
            if success:
                st.success(message)
            else:
                st.warning(message)
        else:
            analyzer._create_sample_data()
            st.info("🔬 Using sample data")
        
        st.markdown("---")
        
        if st.button("🧹 Clean Data", type="primary"):
            if analyzer.df is not None:
                message = analyzer.clean_data()
                st.success("Data cleaned successfully!")
                st.text_area("Cleaning Details", message, height=200)

    # Tabs
    tab_names = ["🏠 Overview", "🔍 Exploration", "🧹 Cleaning", "📈 Analysis", "🔬 Advanced"]
    
    if MATPLOTLIB_AVAILABLE:
        tab_names.append("📊 Charts")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Overview
        st.markdown('<div class="section-header">🏠 Data Overview</div>', unsafe_allow_html=True)
        
        if analyzer.df is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rows", f"{analyzer.df.shape[0]:,}")
            with col2:
                st.metric("Total Columns", analyzer.df.shape[1])
            with col3:
                st.metric("Numeric Columns", len(analyzer.numeric_columns))
            with col4:
                st.metric("Missing Values", analyzer.df.isnull().sum().sum())
            
            st.subheader("👀 Data Preview")
            preview_size = st.slider("Rows to preview", 5, 50, 10)
            st.dataframe(analyzer.df.head(preview_size), use_container_width=True)
    
    with tabs[1]:  # Exploration
        st.markdown('<div class="section-header">🔍 Data Exploration</div>', unsafe_allow_html=True)
        
        if analyzer.df is not None:
            exploration = analyzer.explore_data()
            st.text_area("Exploration Results", exploration, height=250)
            
            st.subheader("📊 Basic Statistics")
            st.dataframe(analyzer.df.describe(), use_container_width=True)
    
    with tabs[2]:  # Cleaning
        st.markdown('<div class="section-header">🧹 Data Cleaning</div>', unsafe_allow_html=True)
        
        if analyzer.df_cleaned is not None:
            st.success("✅ Data is already cleaned!")
            st.subheader("📋 Cleaned Data Preview")
            st.dataframe(analyzer.df_cleaned.head(15), use_container_width=True)
            
            # Download cleaned data
            csv = analyzer.df_cleaned.to_csv(index=False)
            st.download_button(
                label="📥 Download Cleaned Data (CSV)",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
        else:
            st.info("Click 'Clean Data' button in sidebar to clean your data")
    
    with tabs[3]:  # Analysis
        st.markdown('<div class="section-header">📈 Basic Analysis</div>', unsafe_allow_html=True)
        
        if analyzer.df_cleaned is not None:
            analysis_result = analyzer.analyze_data()
            st.text_area("Analysis Results", analysis_result, height=300)
            
            # Correlation matrix
            numeric_df = analyzer.df_cleaned.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1 and MATPLOTLIB_AVAILABLE:
                st.subheader("🔄 Correlation Matrix")
                
                if st.button("Generate Correlation Matrix"):
                    fig, message = analyzer.create_correlation_matrix(numeric_df)
                    
                    if fig is not None:
                        st.success(message)
                        st.pyplot(fig)
                    else:
                        st.error(message)
    
    with tabs[4]:  # Advanced
        st.markdown('<div class="section-header">🔬 Advanced Analysis</div>', unsafe_allow_html=True)
        
        if analyzer.df_cleaned is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔄 Sort Data")
                sort_col = st.selectbox("Select column to sort", analyzer.df_cleaned.columns)
                sort_dir = st.radio("Sort direction", ["Ascending", "Descending"])
                
                if st.button("Sort Data"):
                    sorted_data, message = analyzer.sort_data(sort_col, sort_dir == "Ascending")
                    if sorted_data is not None:
                        st.success(message)
                        st.dataframe(sorted_data.head(15))
            
            with col2:
                st.subheader("📊 Value Counts")
                count_col = st.selectbox("Select column for value counts", analyzer.df_cleaned.columns, key="value_counts")
                value_counts, message = analyzer.get_column_value_counts(count_col)
                
                if value_counts is not None:
                    st.write(f"**Top values in {count_col}:**")
                    for val, count in value_counts.items():
                        st.write(f"- {val}: {count}")
            
            if st.button("Run Full Advanced Analysis"):
                result = analyzer.advanced_analysis()
                st.text_area("Advanced Analysis", result, height=400)
    
    # Charts tab - only show if matplotlib is available
    if MATPLOTLIB_AVAILABLE and len(tabs) > 5:
        with tabs[5]:  # Charts
            st.markdown('<div class="section-header">📊 Charts & Visualizations</div>', unsafe_allow_html=True)
            
            if analyzer.df_cleaned is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    chart_type = st.selectbox(
                        "Chart Type",
                        ["bar", "histogram", "scatter", "line", "box", "pie"]
                    )
                    
                    x_column = st.selectbox("X Axis Column", analyzer.df_cleaned.columns, key="x_axis")
                
                with col2:
                    if chart_type in ['scatter', 'line']:
                        y_column = st.selectbox("Y Axis Column", analyzer.numeric_columns, key="y_axis")
                    else:
                        y_column = None
                    
                    st.write("### Chart Settings")
                
                if st.button("🚀 Create Chart", type="primary"):
                    fig, message = analyzer.create_chart(chart_type, x_column, y_column)
                    
                    if fig is not None:
                        st.success(message)
                        st.pyplot(fig)
                        
                        # Download chart
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
                        buf.seek(0)
                        
                        st.download_button(
                            label="📥 Download Chart",
                            data=buf,
                            file_name="chart.png",
                            mime="image/png"
                        )
                    else:
                        st.error(message)
                
                # Automatic charts
                st.markdown("---")
                st.subheader("🎨 Quick Charts")
                
                if len(analyzer.numeric_columns) > 0:
                    selected_col = st.selectbox("Select numeric column", analyzer.numeric_columns, key="quick_chart_col")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig1, ax1 = plt.subplots(figsize=(8, 5))
                        analyzer.df_cleaned[selected_col].hist(ax=ax1, bins=12, color='lightblue', alpha=0.7)
                        ax1.set_title(f'Distribution of {selected_col}')
                        ax1.set_xlabel(selected_col)
                        st.pyplot(fig1)
                    
                    with col2:
                        fig2, ax2 = plt.subplots(figsize=(8, 5))
                        analyzer.df_cleaned[[selected_col]].boxplot(ax=ax2)
                        ax2.set_title(f'Box Plot of {selected_col}')
                        st.pyplot(fig2)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "📊 Advanced Data Analyzer | Developed with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
