1. Overview

Our group wants to look at how income, poverty, and grocery store access relate to diabetes and obesity rates across U.S. counties. We want to see whether counties with fewer resources also tend to have higher rates of these conditions, and whether grocery access helps explain some of the differences.
We plan to use three public datasets: CDC PLACES for health estimates, the Census American Community Survey (ACS) for income and poverty, and the USDA Food Environment Atlas for grocery store information. We will connect them using county FIPS codes, a shared geographic identifier. First, we'll check each dataset for missing values, inconsistent formats, and other problems. After cleaning those up, we'll combine the data. After the join, we'll assess the combined data again and make graphs and summaries. If we have time, we'll try a basic regression model.
Because IS 477 focuses on data curation, we want someone else to be able to run our work without guessing what we did. We'll write scripts for downloading, cleaning, merging, checking, and analyzing the data, and document any decisions we make. We're looking for associations between county characteristics, not trying to prove that one factor causes a health outcome.

2. Team
   
Each of us will start with a different part of the project, but we'll all check the combined data, work on the reports, and test the final scripts. Our roles may change as we get further into the project.
Timothy: Download and clean CDC PLACES data; help with health analysis and quality checks.
Grace: Download and clean Census ACS income and poverty data; help with the data dictionary.
Eshaan: Download and clean USDA food environment data; help automate the workflow.
Zahi: Lead county FIPS matching, merge the datasets, and check the combined results.
We'll each commit our work to GitHub and write our own short contribution summary for the status report. We'll review one another's work rather than relying only on whoever prepared a dataset.

3. Research or Business Questions

Are lower median household incomes associated with higher estimated diabetes and obesity prevalence?
How are county poverty rates related to these health outcomes?
Does grocery store availability show a relationship with diabetes or obesity after considering income and poverty?
How much county coverage and data quality do we lose when combining information from three agencies?

4. Datasets and Integration Plan
We'll use original government sources rather than datasets reposted on Kaggle.

CDC PLACES: County Data (2024 release)
Source: https://data.cdc.gov/d/fu4u-a9bh  
We'll extract county estimates for diagnosed diabetes and obesity. We'll decide whether to use crude or age-adjusted rates and stick with that choice across both conditions. We'll also check which years the estimates actually describe, since the release year doesn't necessarily match the data year.

Census ACS, 2018–2022 five-year estimates 
Source: https://www.census.gov/data/developers/data-sets/acs-5year.2022.html  
We'll pull median household income (B19013) and use the poverty counts in B17001 to calculate county poverty rates. We'll check for suppressed values and note the margins of error. Census state and county codes can be combined into a five-digit FIPS identifier.

USDA Food Environment Atlas
Source: https://www.ers.usda.gov/data-products/food-environment-atlas  
We'll select a county-level grocery store measure, ideally stores per population. We need to confirm which columns have good coverage and which years they represent before choosing the final variable.

We want the final table to have one row per county, with columns for health, income, poverty, and food access. That way, we can look at all the measures together for the same county. We'll store FIPS codes as five-character strings so leading zeros stay intact. We'll clean the three sources separately, check that each county appears only once, and then join on FIPS. We'll keep track of counties that don't match and look into why before deciding whether to exclude them. We may narrow the geographic scope if nationwide coverage is not reliable.
