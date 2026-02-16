"""
Utils Package
Utility modules for crime analysis dashboard
"""

# Import from original utils module (root level)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from utils_root import (
        apply_custom_styling,
        format_number,
        get_download_button,
        display_kpi_card,
        display_warning_message,
        display_info_message,
        display_success_message,
        display_error_message
    )
except ImportError:
    # Fallback: import directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("utils_root", os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils.py"))
    utils_root = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_root)
    
    apply_custom_styling = utils_root.apply_custom_styling
    format_number = utils_root.format_number
    get_download_button = utils_root.get_download_button
    display_kpi_card = utils_root.display_kpi_card
    display_warning_message = utils_root.display_warning_message
    display_info_message = utils_root.display_info_message
    display_success_message = utils_root.display_success_message
    display_error_message = utils_root.display_error_message

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
