# MODELS2023-ReplicationPackage
Replication package for our paper "Uncertainty-aware consistency checking in industrial settings" by Robbert Jongeling and Antonio Vallecillo, presented at MODELS conference 2023.

## Paper abstract:
Managing inconsistency across models and development artifacts is always a difficult task. The situation is even more complex in large industrial settings, due to some of their practicalities, such as the common use of rather informal models in their designs, the existence of very large sets of loosely connected artifacts, and the difficulty of precisely defining consistency rules among them. Additionally, the development of these large software-intensive systems is riddled with uncertainty, which cannot be avoided. Recent research has focused on means to make certain types of uncertainty explicit and allow reasoning about them. In this work, we explore how we can assist engineers in managing in a lightweight way both consistency and design uncertainty during the creation and maintenance of models and other development artifacts. We identify the types of design uncertainty and inconsistency to be addressed in two concrete industrial settings and show a prototype implementation of our approach to calculating the uncertainty and inconsistency in these cases. We show how making design uncertainty explicit can help tolerate inconsistencies with high uncertainty, prioritize inconsistencies with low associated uncertainty, and uncover previously hidden potential inconsistencies.

## Repository contents:
This repository has the following files:
- `Uncertainty.use` -- This file shows how we use the implementation of subjective logic operators in the modeling tool "USE" to obtain the contents of Table 1 in the paper. The results are then used in LookupTables.py. This USE model makes use of subjective logic operators. Therefore it should be executed with the extended version of USE that supports these operators, which is publically available for download. [Download USE here](https://atenea.lcc.uma.es/downloads/SubjectiveLogic/USE-Uncertainty.zip).
- Implementation -- Folder containing the implementation, including input and output files.
    - Grammars
        - `architecture.tx` -- TextX grammar used to capture the contents of the examples in a uniform way in textual models
        - `uncertainty.tx` -- TextX grammar used to capture the expressions of doubt.
    - Textual models (Input)
        - `SysMLexample.arch` -- Textual model of the setting of example 1, in Figure 1, following architecture.tx.
        - `PLexample.arch` -- Textual model of the setting of example 2, in Figure 2, following architecture.tx.
    - Expressions of degrees of doubt (Input)
        - `Example1-SysML-CPP.uncertainty` -- File containing doubts expressed in example 1, following the grammar defined in uncertainty.tx.
        - `Example2-ProductLine.uncertainty` -- File containing doubts expressed in example 2, following the grammar defined in uncertainty.tx.
    - Code
        - `ConsistencyCheckingInfo.py` -- Contains the consistency rules and propagation rules for degrees of doubt.
        - `Helpers.py` -- Contains some to_string functions
        - `LookupTables.py` -- Instead of directly calling subjective logic operations, we use these lookup tables to simplify the implementation.
        - `UncertaintyCalculations.py` -- In its current form, contains the implementation needed to run the approach for demo 1 and demo 2. Set the variable on line 389 "demo = 1" or "demo = 2" to run demo 1 or demo 2 respectively. The "debug_mode" on line 388 prints fewer uncertainties when set to true, so as to be able to assess manually easier the correctness of the output. Set to False to print all the intermediate results too.
    - Results (Output)
        - `output-example-1.txt` -- Result of running `UncertaintyCalculations.py` with `SysMLexample.arch` and `Example1-SysML-CPP.uncertainty` as input, and when running with the consistency and propagation rules from setting 1 as defined in `ConsistencyCheckingInfo.py`.
        - `output-example-2.txt` -- Result of running `UncertaintyCalculations.py` with `PLexample.arch` and `Example2-ProductLine.uncertainty` as input, and when running with the consistency and propagation rules from setting 2 as defined in `ConsistencyCheckingInfo.py`.

## Following the process described in the paper
If you want to play along while reading the paper, here are the phases to follow:

0. Modeling: The "Textual models" folder contains textual models conforming to the examples in the paper.
1. Annnotating doubts: This is done in files `Example1-SysML-CPP.uncertainty` and `Example2-ProductLine.uncertainty` for example 1 and example 2, respectively. You can edit these files if you want to play around with other expressed doubts.
2. Doubt propagation and combination: UncertaintyCalculations.py takes care of this phase and the next one, see the `main` function and particularly the calls to `get_propagated_uncertainties` for propagation and `get_anded_uncertainties()` for combination.
3. Doubts merge: `UncertaintyCalculations.py` also includes this phase, see the `main` function and particularly the call to `get_merged_uncertainties`
4. Prioritizing inconsistencies: `UncertaintyCalculations.py` also includes this phase, see the `main` function and particularly the calls to `find_inconsistencies` and `get_sorted_inconsitencies`
    
## Python
We're using Python 3.7 and [TextX](https://github.com/textX/textX).



