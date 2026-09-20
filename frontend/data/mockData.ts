// Auto-generated from the app.html prototype's SNAP object.
// Real model output (accuracy, SHAP, RUL) computed against synthetic, physics-informed sensor data.
// See project README for what's real vs. illustrative.
import type { Snapshot } from './types';

export const SNAP: Snapshot = {
  "generated_at": "2026-08-13T14:51:47.023316",
  "model_metrics": {
    "classification_accuracy": 0.9817,
    "classification_sensitivity": 0.8813,
    "confusion_matrix": [
      [
        7835,
        50
      ],
      [
        111,
        824
      ]
    ],
    "rul_mae_hours": 3.4
  },
  "stations": [
    {
      "code": "PS1",
      "name": "Mombasa",
      "lat": -4.0435,
      "lon": 39.6682,
      "km_from_mombasa": 0,
      "pump_count": 3,
      "max_risk": 0.9871,
      "alert": true
    },
    {
      "code": "PS2",
      "name": "Samburu",
      "lat": -3.9667,
      "lon": 39.2167,
      "km_from_mombasa": 62,
      "pump_count": 3,
      "max_risk": 0.0634,
      "alert": false
    },
    {
      "code": "PS3",
      "name": "Maungu",
      "lat": -3.55,
      "lon": 38.7667,
      "km_from_mombasa": 132,
      "pump_count": 3,
      "max_risk": 0.9923,
      "alert": true
    },
    {
      "code": "PS4",
      "name": "Manyani",
      "lat": -3.3167,
      "lon": 38.5,
      "km_from_mombasa": 178,
      "pump_count": 3,
      "max_risk": 0.9529,
      "alert": true
    },
    {
      "code": "PS5",
      "name": "Mtito Andei",
      "lat": -2.6833,
      "lon": 38.1667,
      "km_from_mombasa": 254,
      "pump_count": 3,
      "max_risk": 0.0857,
      "alert": false
    },
    {
      "code": "PS6",
      "name": "Makindu",
      "lat": -2.2833,
      "lon": 37.8333,
      "km_from_mombasa": 318,
      "pump_count": 3,
      "max_risk": 0.1252,
      "alert": false
    },
    {
      "code": "PS7",
      "name": "Sultan Hamud",
      "lat": -1.9333,
      "lon": 37.3333,
      "km_from_mombasa": 368,
      "pump_count": 3,
      "max_risk": 0.9991,
      "alert": true
    },
    {
      "code": "PS8",
      "name": "Konza",
      "lat": -1.7333,
      "lon": 37.1167,
      "km_from_mombasa": 398,
      "pump_count": 2,
      "max_risk": 0.0633,
      "alert": false
    },
    {
      "code": "PS9",
      "name": "Embakasi (JKIA)",
      "lat": -1.3192,
      "lon": 36.9278,
      "km_from_mombasa": 440,
      "pump_count": 2,
      "max_risk": 0.0381,
      "alert": false
    },
    {
      "code": "PS10",
      "name": "Nairobi Terminal",
      "lat": -1.2921,
      "lon": 36.8219,
      "km_from_mombasa": 450,
      "pump_count": 2,
      "max_risk": 0.9994,
      "alert": true
    },
    {
      "code": "PS11",
      "name": "Nakuru Depot",
      "lat": -0.3031,
      "lon": 36.08,
      "km_from_mombasa": 610,
      "pump_count": 2,
      "max_risk": 0.0908,
      "alert": false
    },
    {
      "code": "PS12",
      "name": "Eldoret Depot",
      "lat": 0.5143,
      "lon": 35.2698,
      "km_from_mombasa": 780,
      "pump_count": 3,
      "max_risk": 0.9924,
      "alert": true
    },
    {
      "code": "PS13",
      "name": "Kisumu Depot",
      "lat": -0.1022,
      "lon": 34.7617,
      "km_from_mombasa": 896,
      "pump_count": 3,
      "max_risk": 0.0872,
      "alert": false
    }
  ],
  "pumps": [
    {
      "pump_id": "PS1-P1",
      "station_code": "PS1",
      "risk_probability": 0.0877,
      "health_deviation_index": 0.09,
      "sensors": {
        "vibration_g": 2.17,
        "temperature_c": 72.7,
        "pressure_bar": 4.38,
        "motor_current_a": 40.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1916
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0727
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0534
        },
        {
          "feature": "pressure_bar",
          "value": -0.0518
        },
        {
          "feature": "vibration_g",
          "value": -0.0305
        }
      ],
      "component_states": {
        "bearing": 0.363,
        "impeller": 0.084,
        "seal": 0.553
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS1-P2",
      "station_code": "PS1",
      "risk_probability": 0.034,
      "health_deviation_index": 0.079,
      "sensors": {
        "vibration_g": 2.17,
        "temperature_c": 77,
        "pressure_bar": 4.78,
        "motor_current_a": 45.6
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1923
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0624
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0545
        },
        {
          "feature": "temperature_c_roll_mean",
          "value": -0.0518
        },
        {
          "feature": "vibration_g",
          "value": -0.0357
        }
      ],
      "component_states": {
        "bearing": 0.4,
        "impeller": 0.099,
        "seal": 0.501
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS1-P3",
      "station_code": "PS1",
      "risk_probability": 0.9871,
      "health_deviation_index": 0.257,
      "sensors": {
        "vibration_g": 2.45,
        "temperature_c": 72.6,
        "pressure_bar": 4.98,
        "motor_current_a": 43.4
      },
      "rul_hours": 98.9,
      "rul_ci_low": 94.8,
      "rul_ci_high": 105.4,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.2529
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": 0.199
        },
        {
          "feature": "vibration_g",
          "value": 0.082
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0342
        },
        {
          "feature": "pressure_bar",
          "value": -0.0259
        }
      ],
      "component_states": {
        "bearing": 0.442,
        "impeller": 0.189,
        "seal": 0.369
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Bearing Wear"
    },
    {
      "pump_id": "PS10-P1",
      "station_code": "PS10",
      "risk_probability": 0.9994,
      "health_deviation_index": 0.259,
      "sensors": {
        "vibration_g": 2.68,
        "temperature_c": 70,
        "pressure_bar": 4.79,
        "motor_current_a": 45
      },
      "rul_hours": 94.1,
      "rul_ci_low": 88,
      "rul_ci_high": 99.3,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.2272
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": 0.1936
        },
        {
          "feature": "vibration_g",
          "value": 0.1233
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0348
        },
        {
          "feature": "pressure_bar",
          "value": -0.0201
        }
      ],
      "component_states": {
        "bearing": 0.459,
        "impeller": 0.212,
        "seal": 0.33
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Impeller Imbalance"
    },
    {
      "pump_id": "PS10-P2",
      "station_code": "PS10",
      "risk_probability": 0.0174,
      "health_deviation_index": 0.147,
      "sensors": {
        "vibration_g": 1.95,
        "temperature_c": 75.3,
        "pressure_bar": 5.11,
        "motor_current_a": 36.5
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1133
        },
        {
          "feature": "health_deviation_index",
          "value": -0.1109
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0833
        },
        {
          "feature": "vibration_g",
          "value": -0.0656
        },
        {
          "feature": "pressure_bar",
          "value": -0.0627
        }
      ],
      "component_states": {
        "bearing": 0.423,
        "impeller": 0.164,
        "seal": 0.413
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS11-P1",
      "station_code": "PS11",
      "risk_probability": 0.0908,
      "health_deviation_index": 0.08,
      "sensors": {
        "vibration_g": 1.98,
        "temperature_c": 69.8,
        "pressure_bar": 5.15,
        "motor_current_a": 42.1
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1379
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0943
        },
        {
          "feature": "vibration_g",
          "value": -0.0585
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0541
        },
        {
          "feature": "pressure_bar",
          "value": -0.0462
        }
      ],
      "component_states": {
        "bearing": 0.417,
        "impeller": 0.156,
        "seal": 0.426
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS11-P2",
      "station_code": "PS11",
      "risk_probability": 0.0111,
      "health_deviation_index": 0.042,
      "sensors": {
        "vibration_g": 1.8,
        "temperature_c": 75.1,
        "pressure_bar": 4.65,
        "motor_current_a": 41.6
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1588
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0982
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0844
        },
        {
          "feature": "pressure_bar",
          "value": -0.071
        },
        {
          "feature": "vibration_g",
          "value": -0.0552
        }
      ],
      "component_states": {
        "bearing": 0.398,
        "impeller": 0.131,
        "seal": 0.47
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS12-P1",
      "station_code": "PS12",
      "risk_probability": 0.9924,
      "health_deviation_index": 0.402,
      "sensors": {
        "vibration_g": 2,
        "temperature_c": 75.7,
        "pressure_bar": 3.96,
        "motor_current_a": 41.7
      },
      "rul_hours": 95,
      "rul_ci_low": 88.8,
      "rul_ci_high": 100.7,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.3148
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": 0.1282
        },
        {
          "feature": "pressure_bar",
          "value": 0.0941
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.04
        },
        {
          "feature": "vibration_g",
          "value": -0.027
        }
      ],
      "component_states": {
        "bearing": 0.333,
        "impeller": 0.044,
        "seal": 0.622
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Seal Degradation"
    },
    {
      "pump_id": "PS12-P2",
      "station_code": "PS12",
      "risk_probability": 0.9663,
      "health_deviation_index": 0.119,
      "sensors": {
        "vibration_g": 3.08,
        "temperature_c": 74.1,
        "pressure_bar": 4.03,
        "motor_current_a": 43.2
      },
      "rul_hours": 91.6,
      "rul_ci_low": 80.4,
      "rul_ci_high": 96.1,
      "shap_top_features": [
        {
          "feature": "vibration_g_roll_mean",
          "value": 0.2648
        },
        {
          "feature": "vibration_g",
          "value": 0.1651
        },
        {
          "feature": "health_deviation_index",
          "value": -0.1066
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": 0.0815
        },
        {
          "feature": "pressure_bar",
          "value": 0.06
        }
      ],
      "component_states": {
        "bearing": 0.49,
        "impeller": 0.254,
        "seal": 0.256
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Bearing Wear"
    },
    {
      "pump_id": "PS12-P3",
      "station_code": "PS12",
      "risk_probability": 0.092,
      "health_deviation_index": 0.125,
      "sensors": {
        "vibration_g": 1.99,
        "temperature_c": 70.9,
        "pressure_bar": 4.31,
        "motor_current_a": 37.8
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1644
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0838
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0805
        },
        {
          "feature": "vibration_g",
          "value": -0.0547
        },
        {
          "feature": "temperature_c_roll_mean",
          "value": -0.0054
        }
      ],
      "component_states": {
        "bearing": 0.41,
        "impeller": 0.143,
        "seal": 0.448
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS13-P1",
      "station_code": "PS13",
      "risk_probability": 0.0872,
      "health_deviation_index": 0.104,
      "sensors": {
        "vibration_g": 2.16,
        "temperature_c": 70.9,
        "pressure_bar": 4.12,
        "motor_current_a": 43.9
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1888
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0941
        },
        {
          "feature": "motor_current_a_roll_mean",
          "value": -0.0711
        },
        {
          "feature": "vibration_g",
          "value": -0.0459
        },
        {
          "feature": "motor_current_a",
          "value": -0.027
        }
      ],
      "component_states": {
        "bearing": 0.375,
        "impeller": 0.315,
        "seal": 0.31
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS13-P2",
      "station_code": "PS13",
      "risk_probability": 0.0251,
      "health_deviation_index": 0.09,
      "sensors": {
        "vibration_g": 1.83,
        "temperature_c": 74.4,
        "pressure_bar": 4.9,
        "motor_current_a": 42.1
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1501
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1169
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0662
        },
        {
          "feature": "vibration_g",
          "value": -0.0657
        },
        {
          "feature": "pressure_bar",
          "value": -0.0532
        }
      ],
      "component_states": {
        "bearing": 0.421,
        "impeller": 0.162,
        "seal": 0.417
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS13-P3",
      "station_code": "PS13",
      "risk_probability": 0.016,
      "health_deviation_index": 0.052,
      "sensors": {
        "vibration_g": 2,
        "temperature_c": 74.7,
        "pressure_bar": 4.97,
        "motor_current_a": 41.4
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1653
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0968
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0721
        },
        {
          "feature": "pressure_bar",
          "value": -0.0616
        },
        {
          "feature": "vibration_g",
          "value": -0.0496
        }
      ],
      "component_states": {
        "bearing": 0.399,
        "impeller": 0.131,
        "seal": 0.47
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS2-P1",
      "station_code": "PS2",
      "risk_probability": 0.0634,
      "health_deviation_index": 0.082,
      "sensors": {
        "vibration_g": 1.93,
        "temperature_c": 68.8,
        "pressure_bar": 5.02,
        "motor_current_a": 43.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.141
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1058
        },
        {
          "feature": "vibration_g",
          "value": -0.0671
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0584
        },
        {
          "feature": "pressure_bar",
          "value": -0.039
        }
      ],
      "component_states": {
        "bearing": 0.426,
        "impeller": 0.168,
        "seal": 0.406
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS2-P2",
      "station_code": "PS2",
      "risk_probability": 0.0309,
      "health_deviation_index": 0.19,
      "sensors": {
        "vibration_g": 1.83,
        "temperature_c": 73.4,
        "pressure_bar": 4.42,
        "motor_current_a": 46.5
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1432
        },
        {
          "feature": "vibration_g",
          "value": -0.0803
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0785
        },
        {
          "feature": "pressure_bar",
          "value": -0.0643
        },
        {
          "feature": "health_deviation_index",
          "value": -0.0594
        }
      ],
      "component_states": {
        "bearing": 0.457,
        "impeller": 0.21,
        "seal": 0.333
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS2-P3",
      "station_code": "PS2",
      "risk_probability": 0.0061,
      "health_deviation_index": 0.045,
      "sensors": {
        "vibration_g": 1.93,
        "temperature_c": 76.3,
        "pressure_bar": 4.85,
        "motor_current_a": 40.8
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1663
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0934
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0804
        },
        {
          "feature": "pressure_bar",
          "value": -0.0672
        },
        {
          "feature": "vibration_g",
          "value": -0.0527
        }
      ],
      "component_states": {
        "bearing": 0.395,
        "impeller": 0.127,
        "seal": 0.478
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS3-P1",
      "station_code": "PS3",
      "risk_probability": 0.1386,
      "health_deviation_index": 0.059,
      "sensors": {
        "vibration_g": 2.07,
        "temperature_c": 75.1,
        "pressure_bar": 5.14,
        "motor_current_a": 44.1
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1391
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0971
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0528
        },
        {
          "feature": "vibration_g",
          "value": -0.0523
        },
        {
          "feature": "pressure_bar",
          "value": -0.0412
        }
      ],
      "component_states": {
        "bearing": 0.417,
        "impeller": 0.156,
        "seal": 0.427
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS3-P2",
      "station_code": "PS3",
      "risk_probability": 0.0262,
      "health_deviation_index": 0.074,
      "sensors": {
        "vibration_g": 1.96,
        "temperature_c": 72.5,
        "pressure_bar": 4.68,
        "motor_current_a": 39.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1675
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0976
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.078
        },
        {
          "feature": "pressure_bar",
          "value": -0.0604
        },
        {
          "feature": "vibration_g",
          "value": -0.0496
        }
      ],
      "component_states": {
        "bearing": 0.397,
        "impeller": 0.13,
        "seal": 0.473
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS3-P3",
      "station_code": "PS3",
      "risk_probability": 0.9923,
      "health_deviation_index": 0.489,
      "sensors": {
        "vibration_g": 2.08,
        "temperature_c": 74.4,
        "pressure_bar": 3.86,
        "motor_current_a": 39.8
      },
      "rul_hours": 96.7,
      "rul_ci_low": 92.1,
      "rul_ci_high": 102.4,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.307
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": 0.1149
        },
        {
          "feature": "pressure_bar",
          "value": 0.0884
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0317
        },
        {
          "feature": "vibration_g",
          "value": -0.0232
        }
      ],
      "component_states": {
        "bearing": 0.329,
        "impeller": 0.039,
        "seal": 0.632
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Seal Degradation"
    },
    {
      "pump_id": "PS4-P1",
      "station_code": "PS4",
      "risk_probability": 0.0094,
      "health_deviation_index": 0.084,
      "sensors": {
        "vibration_g": 2,
        "temperature_c": 76.7,
        "pressure_bar": 4.62,
        "motor_current_a": 43.3
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1685
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0993
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0633
        },
        {
          "feature": "pressure_bar",
          "value": -0.0539
        },
        {
          "feature": "vibration_g",
          "value": -0.0506
        }
      ],
      "component_states": {
        "bearing": 0.403,
        "impeller": 0.138,
        "seal": 0.459
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS4-P2",
      "station_code": "PS4",
      "risk_probability": 0.9529,
      "health_deviation_index": 0.421,
      "sensors": {
        "vibration_g": 2.33,
        "temperature_c": 78.2,
        "pressure_bar": 4.28,
        "motor_current_a": 40.8
      },
      "rul_hours": 97.2,
      "rul_ci_low": 93.8,
      "rul_ci_high": 102,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.4354
        },
        {
          "feature": "pressure_bar",
          "value": 0.0384
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0352
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0273
        },
        {
          "feature": "temperature_c_roll_mean",
          "value": 0.017
        }
      ],
      "component_states": {
        "bearing": 0.321,
        "impeller": 0.02,
        "seal": 0.659
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Seal Degradation"
    },
    {
      "pump_id": "PS4-P3",
      "station_code": "PS4",
      "risk_probability": 0.1571,
      "health_deviation_index": 0.104,
      "sensors": {
        "vibration_g": 1.87,
        "temperature_c": 71.5,
        "pressure_bar": 4.19,
        "motor_current_a": 43
      },
      "rul_hours": 158,
      "rul_ci_low": 146.3,
      "rul_ci_high": 165.6,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1854
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1156
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": 0.0615
        },
        {
          "feature": "vibration_g",
          "value": -0.0587
        },
        {
          "feature": "pressure_bar",
          "value": 0.0477
        }
      ],
      "component_states": {
        "bearing": 0.412,
        "impeller": 0.149,
        "seal": 0.44
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS5-P1",
      "station_code": "PS5",
      "risk_probability": 0.0272,
      "health_deviation_index": 0.073,
      "sensors": {
        "vibration_g": 1.67,
        "temperature_c": 72.2,
        "pressure_bar": 4.48,
        "motor_current_a": 40.4
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1595
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1069
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0769
        },
        {
          "feature": "pressure_bar",
          "value": -0.0591
        },
        {
          "feature": "vibration_g",
          "value": -0.0537
        }
      ],
      "component_states": {
        "bearing": 0.406,
        "impeller": 0.141,
        "seal": 0.454
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS5-P2",
      "station_code": "PS5",
      "risk_probability": 0.0857,
      "health_deviation_index": 0.117,
      "sensors": {
        "vibration_g": 2.07,
        "temperature_c": 73.6,
        "pressure_bar": 4.62,
        "motor_current_a": 37.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1471
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0898
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0722
        },
        {
          "feature": "pressure_bar",
          "value": -0.0585
        },
        {
          "feature": "vibration_g",
          "value": -0.0465
        }
      ],
      "component_states": {
        "bearing": 0.399,
        "impeller": 0.132,
        "seal": 0.47
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS5-P3",
      "station_code": "PS5",
      "risk_probability": 0.0136,
      "health_deviation_index": 0.149,
      "sensors": {
        "vibration_g": 1.84,
        "temperature_c": 73.6,
        "pressure_bar": 4.92,
        "motor_current_a": 41.2
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1177
        },
        {
          "feature": "health_deviation_index",
          "value": -0.1062
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0907
        },
        {
          "feature": "vibration_g",
          "value": -0.0661
        },
        {
          "feature": "pressure_bar",
          "value": -0.0652
        }
      ],
      "component_states": {
        "bearing": 0.424,
        "impeller": 0.165,
        "seal": 0.411
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS6-P1",
      "station_code": "PS6",
      "risk_probability": 0.0796,
      "health_deviation_index": 0.117,
      "sensors": {
        "vibration_g": 2.27,
        "temperature_c": 65.8,
        "pressure_bar": 4.62,
        "motor_current_a": 44.1
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1599
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.07
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0641
        },
        {
          "feature": "pressure_bar",
          "value": -0.048
        },
        {
          "feature": "vibration_g",
          "value": -0.0266
        }
      ],
      "component_states": {
        "bearing": 0.379,
        "impeller": 0.105,
        "seal": 0.517
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS6-P2",
      "station_code": "PS6",
      "risk_probability": 0.0244,
      "health_deviation_index": 0.087,
      "sensors": {
        "vibration_g": 1.9,
        "temperature_c": 71.9,
        "pressure_bar": 4.87,
        "motor_current_a": 39.8
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1559
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0996
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0764
        },
        {
          "feature": "pressure_bar",
          "value": -0.0578
        },
        {
          "feature": "vibration_g",
          "value": -0.0571
        }
      ],
      "component_states": {
        "bearing": 0.405,
        "impeller": 0.14,
        "seal": 0.454
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS6-P3",
      "station_code": "PS6",
      "risk_probability": 0.1252,
      "health_deviation_index": 0.083,
      "sensors": {
        "vibration_g": 2.37,
        "temperature_c": 74,
        "pressure_bar": 4.75,
        "motor_current_a": 44.2
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1964
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0674
        },
        {
          "feature": "pressure_bar",
          "value": -0.052
        },
        {
          "feature": "motor_current_a_roll_mean",
          "value": -0.0407
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.0298
        }
      ],
      "component_states": {
        "bearing": 0.313,
        "impeller": 0.115,
        "seal": 0.572
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS7-P1",
      "station_code": "PS7",
      "risk_probability": 0.9991,
      "health_deviation_index": 0.565,
      "sensors": {
        "vibration_g": 2.17,
        "temperature_c": 72.7,
        "pressure_bar": 3.79,
        "motor_current_a": 41.1
      },
      "rul_hours": 94.9,
      "rul_ci_low": 92.2,
      "rul_ci_high": 99.4,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": 0.2574
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": 0.1039
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": 0.0999
        },
        {
          "feature": "pressure_bar",
          "value": 0.0746
        },
        {
          "feature": "vibration_g",
          "value": -0.027
        }
      ],
      "component_states": {
        "bearing": 0.37,
        "impeller": 0.093,
        "seal": 0.537
      },
      "actual_will_fail": true,
      "actual_failure_mode": "Cavitation"
    },
    {
      "pump_id": "PS7-P2",
      "station_code": "PS7",
      "risk_probability": 0.0435,
      "health_deviation_index": 0.126,
      "sensors": {
        "vibration_g": 1.96,
        "temperature_c": 69.3,
        "pressure_bar": 5.08,
        "motor_current_a": 39.2
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1205
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1002
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0829
        },
        {
          "feature": "vibration_g",
          "value": -0.0624
        },
        {
          "feature": "pressure_bar",
          "value": -0.0553
        }
      ],
      "component_states": {
        "bearing": 0.416,
        "impeller": 0.154,
        "seal": 0.43
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS7-P3",
      "station_code": "PS7",
      "risk_probability": 0.0503,
      "health_deviation_index": 0.127,
      "sensors": {
        "vibration_g": 2.18,
        "temperature_c": 78.5,
        "pressure_bar": 3.91,
        "motor_current_a": 44.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.2146
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1152
        },
        {
          "feature": "temperature_c_roll_mean",
          "value": -0.0613
        },
        {
          "feature": "vibration_g",
          "value": -0.0576
        },
        {
          "feature": "pressure_bar",
          "value": 0.0522
        }
      ],
      "component_states": {
        "bearing": 0.428,
        "impeller": 0.138,
        "seal": 0.434
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS8-P1",
      "station_code": "PS8",
      "risk_probability": 0.0093,
      "health_deviation_index": 0.126,
      "sensors": {
        "vibration_g": 1.96,
        "temperature_c": 78.8,
        "pressure_bar": 4.71,
        "motor_current_a": 38.3
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.15
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.114
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0709
        },
        {
          "feature": "vibration_g",
          "value": -0.0695
        },
        {
          "feature": "pressure_bar",
          "value": -0.0583
        }
      ],
      "component_states": {
        "bearing": 0.419,
        "impeller": 0.159,
        "seal": 0.422
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS8-P2",
      "station_code": "PS8",
      "risk_probability": 0.0633,
      "health_deviation_index": 0.092,
      "sensors": {
        "vibration_g": 2.06,
        "temperature_c": 74.3,
        "pressure_bar": 5.19,
        "motor_current_a": 45.8
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.127
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1169
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0661
        },
        {
          "feature": "vibration_g",
          "value": -0.0557
        },
        {
          "feature": "pressure_bar",
          "value": -0.0535
        }
      ],
      "component_states": {
        "bearing": 0.424,
        "impeller": 0.165,
        "seal": 0.412
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS9-P1",
      "station_code": "PS9",
      "risk_probability": 0.0327,
      "health_deviation_index": 0.122,
      "sensors": {
        "vibration_g": 1.93,
        "temperature_c": 70.7,
        "pressure_bar": 4.81,
        "motor_current_a": 41.8
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1386
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.1028
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0738
        },
        {
          "feature": "vibration_g",
          "value": -0.0614
        },
        {
          "feature": "pressure_bar",
          "value": -0.0595
        }
      ],
      "component_states": {
        "bearing": 0.413,
        "impeller": 0.151,
        "seal": 0.436
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    },
    {
      "pump_id": "PS9-P2",
      "station_code": "PS9",
      "risk_probability": 0.0381,
      "health_deviation_index": 0.103,
      "sensors": {
        "vibration_g": 2.02,
        "temperature_c": 76,
        "pressure_bar": 4.41,
        "motor_current_a": 43.7
      },
      "rul_hours": null,
      "rul_ci_low": null,
      "rul_ci_high": null,
      "shap_top_features": [
        {
          "feature": "health_deviation_index",
          "value": -0.1735
        },
        {
          "feature": "vibration_g_roll_mean",
          "value": -0.079
        },
        {
          "feature": "pressure_bar_roll_mean",
          "value": -0.0566
        },
        {
          "feature": "vibration_g",
          "value": -0.0502
        },
        {
          "feature": "pressure_bar",
          "value": -0.0447
        }
      ],
      "component_states": {
        "bearing": 0.396,
        "impeller": 0.128,
        "seal": 0.476
      },
      "actual_will_fail": false,
      "actual_failure_mode": null
    }
  ]
};

export const stations = SNAP.stations;
export const pumps = SNAP.pumps;
export const modelMetrics = SNAP.model_metrics;
