import os
from Traffic_Analysis_System.traffic_analysis import process_csv_data


def test_process_sample_file():
    # Use the sample CSV located in workspace root
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'traffic_data15062024.csv')
    path = os.path.normpath(path)
    outcomes, junction_counts = process_csv_data(path)
    assert outcomes is not None
    assert 'total_vehicles' in outcomes
    assert outcomes['total_vehicles'] > 0
    assert 'total_trucks' in outcomes
    assert 'selected_file' in outcomes
    assert outcomes['selected_file'].endswith('traffic_data15062024.csv')
