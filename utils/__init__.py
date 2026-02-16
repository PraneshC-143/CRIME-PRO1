"""
Utils Package
Utility modules for crime analysis dashboard
"""

# Import utility functions from parent utils.py module
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from root utils.py
import utils as root_utils

apply_custom_styling = root_utils.apply_custom_styling
format_number = root_utils.format_number
get_download_button = root_utils.get_download_button
display_kpi_card = root_utils.display_kpi_card
display_warning_message = root_utils.display_warning_message
display_info_message = root_utils.display_info_message
display_success_message = root_utils.display_success_message
display_error_message = root_utils.display_error_message

from .kpi_calculator import (
    calculate_total_crimes,
    calculate_crime_rate,
    get_most_affected_state,
    get_highest_crime_category,
    calculate_yoy_growth,
    get_top_states_ranking,
    get_trend_indicator,
    calculate_district_kpis,
    calculate_crime_concentration
)

from .map_generator import (
    create_choropleth_map,
    create_bubble_map,
    create_state_heatmap,
    create_treemap,
    create_sunburst
)

from .export_utils import (
    export_to_csv,
    export_chart_as_png,
    create_summary_report,
    prepare_export_data,
    create_yearly_summary,
    create_state_summary,
    create_crime_type_summary
)

__all__ = [
    # Original utils functions
    'apply_custom_styling',
    'format_number',
    'get_download_button',
    'display_kpi_card',
    'display_warning_message',
    'display_info_message',
    'display_success_message',
    'display_error_message',
    
    # KPI functions
    'calculate_total_crimes',
    'calculate_crime_rate',
    'get_most_affected_state',
    'get_highest_crime_category',
    'calculate_yoy_growth',
    'get_top_states_ranking',
    'get_trend_indicator',
    'calculate_district_kpis',
    'calculate_crime_concentration',
    
    # Map functions
    'create_choropleth_map',
    'create_bubble_map',
    'create_state_heatmap',
    'create_treemap',
    'create_sunburst',
    
    # Export functions
    'export_to_csv',
    'export_chart_as_png',
    'create_summary_report',
    'prepare_export_data',
    'create_yearly_summary',
    'create_state_summary',
    'create_crime_type_summary'
]
