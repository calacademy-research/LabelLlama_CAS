---
name: associatedTaxa
description: Extract label text describing other named plants, fungi, animals, or taxa that occur with, near, under, over, on, or otherwise in ecological or spatial association with the collected specimen.
module: llama/fields/occurrence/associatedTaxa.py
---

# Prompt associatedTaxa

`associatedTaxa` (str): Extract label text describing OTHER named taxa that occur in an ecological, biological, or spatial relationship with the collected specimen.

Only extract taxa when the label indicates that they occur with, near, under, among, on, adjacent to, or in the surrounding vegetation/community of the specimen.

Examples of valid context:
- "with Artemisia vulgaris"
- "growing under Quercus agrifolia and Aesculus californica"
- "common plants include..."
- "also present..."
- "Pinus sabiniana and Quercus douglasii the common dominants"
- "Rhus diversiloba ... common shrubs in the understory"
- "Douglas fir forest"
- host, substrate, parasite, pollinator, or symbiotic relationships

IMPORTANT: A second taxon name appearing on the label is NOT by itself evidence of associated taxa.

Do NOT extract taxa that occur only as:
- the specimen's identification
- determination or annotation labels
- previous or revised identifications
- synonyms or alternative names
- hybrid parentage
- taxonomic comparisons ("similar to", "related to")
- family names or other identification metadata

For example:

"Gaillardia x grandiflora. Hybrid between G. aristata and G. pulchella."
→ ""

"Hoita macrostachya ... Det. James Grimes ... Psoralea macrostachya DC."
→ ""

"Growing with Rhus diversiloba, Rosa californica."
→ "Growing with Rhus diversiloba, Rosa californica."

Preserve the original wording of the association as closely as possible. Do not reduce it to a normalized list of taxon names. Retain useful ecological wording such as "forest", "dominant", "understory", "with", "beneath", "also present", etc.

Remove unrelated locality, date, collector, elevation, and specimen-description text.

When uncertain whether another taxon is an ecological associate or merely another identification of the specimen, return an empty string.

If no associated taxa are mentioned, return an empty string.