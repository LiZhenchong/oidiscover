import streamlit as st
import pandas as pd
import json
import requests
import io
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import warnings

# Configure matplotlib for Chinese font support
def setup_chinese_font():
    """Setup Chinese font for matplotlib"""
    try:
        # Get available fonts
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # Try to find a Chinese font
        chinese_fonts = [
            'SimHei',  # Windows
            'STHeiti',  # macOS
            'PingFang SC',  # macOS
            'Hiragino Sans GB',  # macOS
            'WenQuanYi Micro Hei',  # Linux
            'Noto Sans CJK SC',  # Linux
            'DejaVu Sans',  # Fallback
        ]
        
        found_font = None
        for font in chinese_fonts:
            if font in available_fonts:
                found_font = font
                break
        
        if found_font:
            plt.rcParams['font.sans-serif'] = [found_font]
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.family'] = 'sans-serif'
        else:
            # If no Chinese font found, suppress the warnings
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            plt.rcParams['axes.unicode_minus'] = False
        
    except Exception:
        # Suppress font warnings
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Setup font when module loads
setup_chinese_font()

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = 'sk-5b8931fa8b954025a3443faa16867476'

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_code' not in st.session_state:
    st.session_state.current_code = ""

if 'execution_results' not in st.session_state:
    st.session_state.execution_results = []

# Deepseek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def clean_dataframe(df):
    """Clean dataframe for better compatibility with Streamlit"""
    df_clean = df.copy()
    
    # Clean column names
    df_clean.columns = [str(col).strip().replace('\n', ' ').replace('\r', ' ') for col in df_clean.columns]
    
    # Process each column
    for col in df_clean.columns:
        try:
            column_data = df_clean[col]
            
            if column_data.dtype == 'object':
                def safe_str_convert(x):
                    if pd.isna(x) or x is None:
                        return ''
                    elif isinstance(x, (list, dict, tuple)):
                        return str(x)
                    else:
                        return str(x)
                
                df_clean[col] = column_data.apply(safe_str_convert)
                
            elif column_data.dtype in ['int64', 'float64', 'int32', 'float32']:
                df_clean[col] = column_data.fillna(0)
                
            elif 'datetime' in str(column_data.dtype):
                df_clean[col] = column_data.astype(str)
                
            else:
                df_clean[col] = column_data.astype(str)
                
        except Exception as e:
            st.warning(f"Converting column '{col}' to string due to data type issues: {str(e)}")
            df_clean[col] = df_clean[col].apply(lambda x: str(x) if x is not None else '')
    
    # Final PyArrow compatibility check
    for col in df_clean.columns:
        try:
            import pyarrow as pa
            pa.array(df_clean[col])
        except Exception:
            def ultra_clean(x):
                if x is None or pd.isna(x):
                    return ''
                try:
                    s = str(x)
                    s = s.replace('\x00', '').replace('\n', ' ').replace('\r', ' ')
                    s = ''.join(char for char in s if ord(char) >= 32 or char in '\t\n\r')
                    return s[:100]  # Limit length
                except:
                    return ''
            
            df_clean[col] = df_clean[col].apply(ultra_clean)
    
    # Remove completely empty columns
    df_clean = df_clean.dropna(axis=1, how='all')
    
    return df_clean

def load_data(uploaded_file):
    """Load data from various file formats"""
    if uploaded_file is None:
        return None

    file_extension = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == 'xlsx':
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif file_extension == 'json':
            df = pd.read_json(uploaded_file)
        else:
            st.error('Unsupported file format. Please upload CSV, Excel, or JSON file.')
            return None
        
        # Clean data for better compatibility
        df = clean_dataframe(df)
        return df
    except Exception as e:
        st.error(f'Error loading file: {str(e)}')
        return None

def get_data_summary(df):
    """Generate a summary of the dataset"""
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    summary = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'info': info_str,
        'description': df.describe().to_dict()
    }
    return summary

def call_deepseek_api(messages):
    """Call Deepseek API"""
    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": messages
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error calling Deepseek API: {str(e)}")
        return None

def analyze_with_ai(df, user_query, conversation_history=None):
    """Use Deepseek to analyze the data based on user query"""
    data_summary = get_data_summary(df)

    system_prompt = """You are a data analysis expert. Analyze the provided data according to the user's query.
    Generate Python code using pandas, matplotlib, and seaborn for visualization if needed.
    Consider the conversation history to provide contextual responses.
    Return your response in the following JSON format:
    {
        "analysis": "Your analysis explanation",
        "code": "Python code to generate the analysis/visualization",
        "visualization_needed": true/false
    }
    """

    user_message = f"""
    Data Summary:
    {json.dumps(data_summary, indent=2)}

    User Query:
    {user_query}

    Please analyze this data and provide insights.
    """

    # Build messages with conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    if conversation_history:
        for item in conversation_history[-5:]:  # Keep last 5 interactions
            messages.append({"role": "user", "content": item.get("query", "")})
            if item.get("response"):
                messages.append({"role": "assistant", "content": item["response"]})
    
    messages.append({"role": "user", "content": user_message})

    try:
        response = call_deepseek_api(messages)
        if response and 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            if content and content.strip():
                # Extract JSON from markdown code blocks if present
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    if json_end != -1:
                        content = content[json_start:json_end].strip()
                
                return json.loads(content)
        st.error("Empty or invalid response from API")
        return None
    except Exception as e:
        st.error(f"Error in AI analysis: {str(e)}")
        return None

def execute_code(code, df):
    """Execute code safely and return output"""
    try:
        # Setup font for execution
        setup_chinese_font()
        
        # Create a safe context for code execution
        local_vars = {
            'pd': pd,
            'plt': plt,
            'sns': sns,
            'df': df,
            'print': lambda *args: st.write(' '.join(str(arg) for arg in args))
        }
        
        # Capture output
        from contextlib import redirect_stdout
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            exec(code, globals(), local_vars)
        
        output = output_buffer.getvalue()
        return output, True
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        st.error(error_msg)
        return error_msg, False

def display_dataframe(df):
    """Display dataframe with multiple fallback methods"""
    display_success = False
    
    # Try 1: Standard dataframe display
    try:
        st.dataframe(df.head())
        display_success = True
    except Exception as e:
        st.warning(f"Interactive dataframe failed: {str(e)}")
    
    # Try 2: Force all columns to string and try again
    if not display_success:
        try:
            df_display = df.head().copy()
            for col in df_display.columns:
                df_display[col] = df_display[col].astype(str)
            st.dataframe(df_display)
            display_success = True
        except Exception as e:
            st.warning(f"String conversion dataframe failed: {str(e)}")
    
    # Try 3: HTML table
    if not display_success:
        try:
            st.write("Showing data as HTML table:")
            st.write(df.head().to_html(escape=False), unsafe_allow_html=True)
            display_success = True
        except Exception as e:
            st.warning(f"HTML display failed: {str(e)}")
    
    # Final fallback - text display
    if not display_success:
        st.write("Showing data as text:")
        st.text(df.head().to_string())

def main():
    # Set page config
    st.set_page_config(
        page_title="AI Data Explorer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("AI Data Explorer")

    # Sidebar
    with st.sidebar:
        st.header("API Configuration")
        st.info(f"Using Deepseek API Key: ...{st.session_state.api_key[-4:]}")
        
        st.header("Session Controls")
        if st.button("🗑️ Clear All History"):
            st.session_state.conversation_history = []
            st.session_state.current_code = ""
            st.session_state.execution_results = []
            if hasattr(st.session_state, 'latest_followup'):
                del st.session_state.latest_followup
            st.rerun()

    st.write("Upload your data file and ask questions about it!")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file (CSV, Excel, or JSON)",
        type=['csv', 'xlsx', 'json']
    )

    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)

        if df is not None:
            # Use tabs to organize content
            tab1, tab2, tab3 = st.tabs(["📊 Data Overview", "💬 Analysis", "📋 History"])
            
            with tab1:
                st.write("### Data Preview")
                display_dataframe(df)

                st.write("### Data Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", df.shape[0])
                with col2:
                    st.metric("Columns", df.shape[1])
                
                # Show column info
                with st.expander("Column Details"):
                    try:
                        st.write("**Data Types:**")
                        st.write(df.dtypes)
                        st.write("**Sample Values:**")
                        for col in df.columns[:5]:  # Show first 5 columns
                            st.write(f"**{col}**: {df[col].head(3).tolist()}")
                    except Exception as e:
                        st.error(f"Error displaying column details: {str(e)}")
            
            with tab3:
                # Show conversation history
                if st.session_state.conversation_history:
                    st.write("### Conversation History")
                    for i, item in enumerate(st.session_state.conversation_history[-5:]):
                        with st.expander(f"Query {len(st.session_state.conversation_history) - 5 + i + 1}: {item['query'][:50]}..."):
                            st.write("**Query:**", item['query'])
                            if item.get('analysis'):
                                st.write("**Analysis:**", item['analysis'])
                            if item.get('code'):
                                st.code(item['code'], language="python")
                            if item.get('output'):
                                st.write("**Output:**", item['output'])
                else:
                    st.info("No conversation history yet. Start by asking a question in the Analysis tab!")
            
            with tab2:
                # User query input
                user_query = st.text_area(
                    "What would you like to know about this data?",
                    "Please analyze the trends in this dataset."
                )

                col1, col2 = st.columns(2)
                with col1:
                    analyze_button = st.button("Analyze", type="primary")
                with col2:
                    clear_history = st.button("Clear History")

                if clear_history:
                    st.session_state.conversation_history = []
                    st.session_state.current_code = ""
                    st.session_state.execution_results = []
                    st.rerun()

                # Main analysis
                if analyze_button and user_query:
                    with st.spinner("Analyzing data..."):
                        analysis_result = analyze_with_ai(df, user_query, st.session_state.conversation_history)

                        if analysis_result:
                            # Display analysis results
                            st.write("### Analysis Results")
                            st.write(analysis_result["analysis"])
                            
                            # Display generated code
                            st.write("### Generated Code")
                            st.code(analysis_result["code"], language="python")
                            
                            # Execute code
                            st.write("### Execution Results")
                            output, success = execute_code(analysis_result["code"], df)
                            
                            if success and output:
                                st.text(output)
                            
                            # Show visualization if needed
                            if analysis_result.get("visualization_needed", False):
                                plt.figure(figsize=(10, 6))
                                st.pyplot(plt)
                                plt.close()
                            
                            # Add to conversation history
                            st.session_state.conversation_history.append({
                                'query': user_query,
                                'analysis': analysis_result["analysis"],
                                'code': analysis_result["code"],
                                'output': output,
                                'response': f"Analysis: {analysis_result['analysis']}\nCode: {analysis_result['code']}"
                            })
                            
                            # Follow-up section
                            st.write("### Follow-up Questions")
                            with st.form("followup_form"):
                                followup_query = st.text_input(
                                    "Ask a follow-up question:",
                                    placeholder="e.g., Can you show this as a percentage?"
                                )
                                
                                followup_submit = st.form_submit_button("Ask Follow-up")
                                
                                if followup_submit and followup_query:
                                    with st.spinner("Processing follow-up..."):
                                        followup_result = analyze_with_ai(df, followup_query, st.session_state.conversation_history)
                                        
                                        if followup_result:
                                            st.write("#### Follow-up Analysis")
                                            st.write(followup_result["analysis"])
                                            
                                            st.write("#### Follow-up Code")
                                            st.code(followup_result["code"], language="python")
                                            
                                            # Execute follow-up code
                                            st.write("#### Follow-up Results")
                                            followup_output, followup_success = execute_code(followup_result["code"], df)
                                            
                                            if followup_success and followup_output:
                                                st.text(followup_output)
                                            
                                            # Show visualization if needed
                                            if followup_result.get("visualization_needed", False):
                                                plt.figure(figsize=(10, 6))
                                                st.pyplot(plt)
                                                plt.close()
                                            
                                            # Add follow-up to history
                                            st.session_state.conversation_history.append({
                                                'query': followup_query,
                                                'analysis': followup_result["analysis"],
                                                'code': followup_result["code"],
                                                'output': followup_output,
                                                'response': f"Analysis: {followup_result['analysis']}\nCode: {followup_result['code']}"
                                            })
                            
                            # Code editor
                            with st.expander("✏️ Code Editor", expanded=False):
                                st.write("Edit and re-execute the generated code:")
                                
                                edited_code = st.text_area(
                                    "Edit the code:",
                                    value=analysis_result["code"],
                                    height=200,
                                    key="code_editor"
                                )
                                
                                if st.button("Execute Modified Code", key="execute_modified"):
                                    st.write("#### Modified Code Results")
                                    modified_output, modified_success = execute_code(edited_code, df)
                                    
                                    if modified_success and modified_output:
                                        st.text(modified_output)
                                    
                                    # Show visualization
                                    plt.figure(figsize=(10, 6))
                                    st.pyplot(plt)
                                    plt.close()

if __name__ == "__main__":
    main()