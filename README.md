Initial Data  
All ​​510,079 firms in Orbis in Germany  
All 199,854 firms in Kununu in Germany

Filtering Data  
Considered only Orbis firms with more than 30 employees and Kununu firms with more than 10 reviews. This leaves 128,403 Orbis and 38,512 Kununu firms.

Preprocessing Data

* Replace umlauts with Latin alphabet characters  
* Put everything in lowercase  
* Remove special characters  
* When two Kununu firms have the same name, keep the one with the most reviews

Merging

1. Merge exact matches in names (merges roughly 14,000 firms)  
2. Change vowels (e.g. replace “ae” with “a”) and merge remaining names (merges roughly 2,100 firms)  
3. Remove company-type appendices (e.g. “gmbh”) and merge only if there are no other firms with the same name after removing the appendix (merges roughly 1,400 firms). For example, if “heinz ag” and “heinz gmbh” are firms in Orbis, none of these firms will be merged with “heinz” in orbis.

So we’ve merged roughly 45% of firms in Kununu.

Fuzzy Merging

* For the remaining firms, compute the [normalized Indel distance](https://maxbachmann.github.io/RapidFuzz/Usage/distance/Indel.html) (i.e. how many characters need to be moved or deleted to get from one name to another, normalized by name length). Exclude appendices (e.g. “gmbh”), as well as common words like “international” from calculation.[^1] Then, manually select between matches that have a score above 95\.  
  * There are roughly 13,800 potential matches. I estimate about half of these are true matches.  
  * I also estimate that verifying these matches will very roughly take about 40 hours of work.

[^1]:  A “common” word is a word that appears more than 40 times across all Orbis and Kununu names. Without removing these words, the “close matches” are filled with companies that share a common word (e.g. “business” or “holding”) but have nothing else in common. 