# Methodology and model boundaries

## Planning complexity index

The portfolio view assigns a 0-100 screening score using only public project metadata. Factors include disclosed project value, number of disclosed funding sources, delivery stage, proximity or passage of target completion date, infrastructure category and missing location metadata.

The score is designed for triage. It is not a prediction of delay, cost overrun, failure or procurement outcome.

## Procurement matching

The Procurement Radar creates candidate links between Toronto's advance Capital Projects Pipeline and currently open Toronto Bids solicitations. Text is normalized, common procurement words are removed and candidate pairs are ranked with a weighted combination of token overlap and sequence similarity. A same-division match adds a small bonus.

These links are analyst aids only. The City of Toronto remains the authoritative source for whether a solicitation corresponds to a particular planned capital project.

## Budget aggregation

The dashboard sums only values disclosed in the Ontario Builds dataset. Many projects do not publish a budget, therefore the aggregate must not be interpreted as Ontario's complete infrastructure plan.
