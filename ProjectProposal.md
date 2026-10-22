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
