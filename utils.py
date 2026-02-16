import streamlit as st
import pandas as pd


def apply_custom_styling():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
        <style>
        .main {
            background-color: #fafafa;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #f0f2f6;
            border-radius: 5px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)


def format_number(value):
    """Format a number with thousands separator"""
    if isinstance(value, (int, float)):
        return f'{value:,}'
    return value


def get_download_button(data, filename):
    """Create a download button for given data"""
    csv = data.to_csv(index=False)
    st.download_button(
        label='📥 Download CSV',
        data=csv,
        file_name=f"{filename}.csv",
        mime='text/csv'
    )


def display_kpi_card(title, value, icon=""):
    """Display a Key Performance Indicator (KPI) card with optional icon"""
    formatted_value = format_number(value) if isinstance(value, (int, float)) else value
    st.metric(label=f"{icon} {title}" if icon else title, value=formatted_value)


def display_warning_message(message):
    """Display a warning message"""
    st.warning(f'⚠️ {message}')


def display_info_message(message):
    """Display an info message"""
    st.info(f'ℹ️ {message}')


def display_success_message(message):
    """Display a success message"""
    st.success(f'✅ {message}')


def display_error_message(message):
    """Display an error message"""
    st.error(f'❌ {message}')


def format_crime_name(crime_name):
    """
    Convert database crime names to human-readable format.
    
    Examples:
        murder_section_302_ipc -> Murder
        theft_section_379_ipc -> Theft
        kidnapping_and_abduction_section_363_to_373_ipc -> Kidnapping and Abduction
        clpbl_hmcrd_not_amt_murder -> Culpable Homicide Not Amounting to Murder
    
    Args:
        crime_name (str): Raw crime name from database
        
    Returns:
        str: Formatted, human-readable crime name
    """
    if not crime_name or not isinstance(crime_name, str):
        return crime_name
    
    import re
    
    # Remove IPC section references (anything with 'section' and numbers)
    # Pattern: _section_XXX_ipc or _section_XXX_to_XXX_ipc
    cleaned = re.sub(r'_section_\d+(_to_\d+)?_ipc', '', crime_name)
    
    # Replace specific abbreviations and shortened words
    # Split by underscore, replace abbreviations, then rejoin
    parts = cleaned.split('_')
    
    # Abbreviation mapping
    abbreviation_map = {
        'clpbl': 'culpable',
        'hmcrd': 'homicide',
        'amt': 'amounting',
        'acdnt': 'accident',
        'negnc': 'negligence',
        'negl': 'negligence',
        'neg': 'negligence',
        'rel': 'related',
        'rail': 'railway',
        'med': 'medical',
        'atmpt': 'attempt',
        'cmmt': 'commit',
        'clpb': 'culpable',
        'miscarr': 'miscarriage',
        'foetic': 'foetal',
        'aband': 'abandonment',
        'vlntrly': 'voluntarily',
        'caus': 'causing',
        'pub': 'public',
        'srvnt': 'servant',
        'hrt': 'hurt',
        'endgrng': 'endangering',
        'lf': 'life',
        'grvus': 'grievous',
        'wepn': 'weapon',
        'sex': 'sexual',
        'hrrsmt': 'harassment',
        'prms': 'premises',
        'trnsprt': 'transport',
        'sys': 'system',
        'frgn': 'foreign',
        'cntry': 'country',
        'kidnp': 'kidnapping',
        'abduc': 'abduction',
        'ofnc': 'offence',
        'agnst': 'against',
        'trnqul': 'tranquility',
        'elec': 'election',
        'pwr': 'power',
        'disp': 'dispute',
        'polc': 'police',
        'prsnl': 'personnel',
        'gvt': 'government',
        'impt': 'import',
        'asrtns': 'assertions',
        'prjudc': 'prejudice',
        'intgrtn': 'integration',
        'mkng': 'making',
        'prprtn': 'preparation',
        'assmbly': 'assembly',
        'cmmttng': 'committing',
        'dcty': 'dacoity',
        'dsh': 'dishonestly',
        'hon': 'honest',
        'rec': 'receiving',
        'deal': 'dealing',
        'stl': 'stolen',
        'prop': 'property',
        'cntrft': 'counterfeit',
        'curr': 'currency',
        'disbnc': 'disobedience',
        'ordr': 'order',
        'prmlgtd': 'promulgated',
        'pblc': 'public',
        'rsh': 'rash',
        'nglgnt': 'negligent',
        'drvng': 'driving',
        'wy': 'way',
        'csng': 'causing',
        'crcl': 'circulating',
        'sec': 'section',
    }
    
    # Replace each part if it's an abbreviation
    replaced_parts = [abbreviation_map.get(part.lower(), part) for part in parts if part]
    
    # Join with spaces
    cleaned = ' '.join(replaced_parts)
    
    # Convert to title case
    cleaned = cleaned.title()
    
    # Handle special cases that need uppercase
    special_cases = {
        'Ipc': 'IPC',
        'Sc': 'SC',
        'St': 'ST',
        'Ndps': 'NDPS',
        'It': 'IT',
        'Crpc': 'CrPC',
    }
    
    for old, new in special_cases.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned.strip()
