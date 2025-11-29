--- Starting Feature Importance Analysis ---

Analyzing LogisticRegression...
   Spearman Corr (Imp vs Std): 0.9140
   Top 5 Robust Features (High R):
A	B	C	Mean_Imp	Std_Imp	Robustness_R
url_length	0.1096	0.0184	0.2292	0.119067	0.105718	0.107683
path_length	0.0396	0.0140	0.3080	0.120533	0.162855	0.103653
ratio_external_links	0.0940	0.0476	0.0192	0.053600	0.037759	0.051650
num_dots	0.0588	0.0580	0.0028	0.039867	0.032103	0.038627
hostname_length	0.0552	0.0492	0.0140	0.039467	0.022258	0.038607



Analyzing RandomForest...
   Spearman Corr (Imp vs Std): 0.9061
   Top 5 Robust Features (High R):
A	B	C	Mean_Imp	Std_Imp	Robustness_R
ratio_external_links	0.1624	0.1524	0.0828	0.132533	0.043360	0.127026
ratio_null_links	0.0728	0.0000	0.0476	0.040133	0.036970	0.038703
num_numeric_chars	0.0124	0.0788	0.0276	0.039600	0.034789	0.038269
path_length	0.0024	0.0460	0.0640	0.037467	0.031674	0.036316
path_depth	0.0056	0.0772	0.0168	0.033200	0.038514	0.031969


Analyzing FT-Transformer...
Training FT-Transformer for 15 epochs...
Training FT-Transformer for 15 epochs...
Training FT-Transformer for 15 epochs...
   Spearman Corr (Imp vs Std): 0.8984
   Top 5 Robust Features (High R):
A	B	C	Mean_Imp	Std_Imp	Robustness_R
ratio_external_links	0.1492	0.0664	0.0460	0.087200	0.054654	0.082681
path_length	0.0060	0.0240	0.1236	0.051200	0.063343	0.048150
path_depth	0.0200	0.0940	0.0204	0.044800	0.042609	0.042969
num_numeric_chars	0.0160	0.0624	0.0400	0.039467	0.023205	0.038572
ratio_null_links	0.0720	0.0000	0.0284	0.033467	0.036266	0.032295
