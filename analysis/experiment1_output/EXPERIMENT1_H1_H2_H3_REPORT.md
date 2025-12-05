# Experiment 1: CoT Length Analysis Results

## Hypotheses Tested

- **H1**: Longer CoT traces reduce Overseer accuracy
- **H2**: Length effect is stronger for werewolves than villagers
- **H3**: Effect is mediated by JUSTIFICATION and PLAN counts

## 1. Descriptive Statistics

### 1.1 CoT Length by Role

| player_role   |   ('cot_length_sent', 'mean') |   ('cot_length_sent', 'std') |   ('cot_length_sent', 'min') |   ('cot_length_sent', 'max') |   ('cot_length_tokens', 'mean') |   ('cot_length_tokens', 'std') |
|:--------------|------------------------------:|-----------------------------:|-----------------------------:|-----------------------------:|--------------------------------:|-------------------------------:|
| FortuneTeller |                          4.74 |                         1.52 |                            3 |                            6 |                           56.63 |                          17.77 |
| Villager      |                          4.05 |                         1.44 |                            2 |                            6 |                           49.07 |                          20.33 |
| Werewolf      |                          5.53 |                         1.12 |                            3 |                            6 |                           73.84 |                          17    |


### 1.2 Werewolves: Caught vs Missed

|   caught |   ('cot_length_sent', 'mean') |   ('cot_length_sent', 'std') |   ('justification_count', 'mean') |   ('justification_count', 'std') |   ('plan_count', 'mean') |   ('plan_count', 'std') |   ('deception_strategy_count', 'mean') |   ('deception_strategy_count', 'std') |
|---------:|------------------------------:|-----------------------------:|----------------------------------:|---------------------------------:|-------------------------:|------------------------:|---------------------------------------:|--------------------------------------:|
|        0 |                          5.25 |                         1.36 |                              0.83 |                             0.72 |                     1.25 |                    0.75 |                                   1.83 |                                  1.8  |
|        1 |                          6    |                         0    |                              0.43 |                             0.53 |                     1.71 |                    0.76 |                                   2.29 |                                  1.11 |


### 1.3 Villagers: Accused vs Cleared

|   accused |   ('cot_length_sent', 'mean') |   ('cot_length_sent', 'std') |   ('justification_count', 'mean') |   ('justification_count', 'std') |   ('plan_count', 'mean') |   ('plan_count', 'std') |   ('assertion_count', 'mean') |   ('assertion_count', 'std') |
|----------:|------------------------------:|-----------------------------:|----------------------------------:|---------------------------------:|-------------------------:|------------------------:|------------------------------:|-----------------------------:|
|         0 |                          4.03 |                         1.44 |                              0.27 |                             0.45 |                     1.67 |                    0.74 |                           1.8 |                         1.06 |
|         1 |                          5.25 |                         1.36 |                              0.42 |                             0.51 |                     2.08 |                    0.9  |                           2   |                         0.74 |


### 1.4 Correlation: Length and Tag Counts

|                     |   cot_length_sent |   justification_count |   plan_count |   assertion_count |
|:--------------------|------------------:|----------------------:|-------------:|------------------:|
| cot_length_sent     |             1     |                 0.295 |        0.463 |             0.508 |
| justification_count |             0.295 |                 1     |       -0.249 |            -0.117 |
| plan_count          |             0.463 |                -0.249 |        1     |             0.271 |
| assertion_count     |             0.508 |                -0.117 |        0.271 |             1     |


## 2. Regression Results

### Model 1: Length + Role + Interaction

```
                                  Logit Regression Results                                  
============================================================================================
Dep. Variable:     overseer_correct_for_this_player   No. Observations:                   95
Model:                                        Logit   Df Residuals:                       91
Method:                                         MLE   Df Model:                            3
Date:                              Fri, 21 Nov 2025   Pseudo R-squ.:                  0.2433
Time:                                      00:00:56   Log-Likelihood:                -40.632
converged:                                     True   LL-Null:                       -53.695
Covariance Type:                          nonrobust   LLR p-value:                 8.978e-06
=================================================================================================
                                    coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------------------
Intercept                         1.7790      0.361      4.927      0.000       1.071       2.487
cot_length_z                     -0.8894      0.366     -2.433      0.015      -1.606      -0.173
is_true_werewolf                -21.5505        nan        nan        nan         nan         nan
cot_length_z:is_true_werewolf    20.3076        nan        nan        nan         nan         nan
=================================================================================================
```

### Model 2: + JUSTIFICATION + PLAN (Mediators)

```
                                  Logit Regression Results                                  
============================================================================================
Dep. Variable:     overseer_correct_for_this_player   No. Observations:                   95
Model:                                        Logit   Df Residuals:                       89
Method:                                         MLE   Df Model:                            5
Date:                              Fri, 21 Nov 2025   Pseudo R-squ.:                  0.2644
Time:                                      00:00:56   Log-Likelihood:                -39.500
converged:                                    False   LL-Null:                       -53.695
Covariance Type:                          nonrobust   LLR p-value:                 3.053e-05
=================================================================================================
                                    coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------------------
Intercept                         1.7765      0.369      4.820      0.000       1.054       2.499
cot_length_z                     -0.7678      0.439     -1.750      0.080      -1.628       0.092
is_true_werewolf                -17.4946   1.56e+06  -1.12e-05      1.000   -3.06e+06    3.06e+06
cot_length_z:is_true_werewolf    16.4327   1.55e+06   1.06e-05      1.000   -3.04e+06    3.04e+06
justification_z                  -0.4330      0.310     -1.395      0.163      -1.041       0.175
plan_z                           -0.0596      0.355     -0.168      0.867      -0.756       0.637
=================================================================================================
```

## 3. Hypothesis Testing Results

### H1: Does length hurt overall?

- **Model 1** β_length = -0.889, p = 0.015
- **Model 2** β_length = -0.768, p = 0.080
- **Mediation effect**: -0.122
- **Conclusion**: ✅ SUPPORTED

### H2: Is length worse for werewolves?

- **Model 1** β_interaction = 20.308, p = nan
- **Model 2** β_interaction = 16.433, p = 1.000
- **Conclusion**: ❌ NOT SUPPORTED

### H3: Is effect mediated by JUSTIFICATION/PLAN?

- **β_JUSTIFICATION** = -0.433, p = 0.163
- **β_PLAN** = -0.060, p = 0.867
- **Length coefficient shrinkage**: -13.7%
- **Conclusion**: ⚠️ PARTIAL SUPPORT

## 4. Interpretation

TBD: Add interpretation based on results
