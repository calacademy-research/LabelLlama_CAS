
---
name: habitat
description: Extract habitat information from the text.
module: llama/fields/event/habitat.py
---

# Prompt Habitat

`habitat` (str): Extract only text that explicitly describes the physical environment or ecological setting where the specimen grows or was collected. 
It describes the surrounding environment as if you were dropped there randomly without a map, so no proper place names , distances, however physical descriptions of the surrounding environment or biome. These can include things like measurements of soil ph or water levels.

## Habitat versus locality

- Habitat describes WHAT THE ENVIRONMENT IS LIKE: soil, substrate, moisture, vegetation, disturbance, land use, or microhabitat.
- Locality describes WHERE THE COLLECTION SITE IS: named places or features, addresses, routes, distances, bearings, or directions for finding the site.
- Generic environmental phrases such as “along road”, “on hills”, “on canyon slopes”, “stream bank”, and “trail edge” are habitat when they describe the immediate growing environment.
- Named features and locating phrases such as “along Highway 395”, “near McGee Creek”, “above Glen Alpine”, and “3 miles west of Jacumba” are locality.
- Unnamed references can also be locality: “near the bridge” and “2 km upstream from the road junction” locate a site without describing its habitat.
- Slope aspect describes habitat: retain “north-facing slopes”. A bearing locates a site: exclude “north of the mountain”.

## Include

- Soil and substrate: dry sand, loamy soil, gravel, calcareous rock, peat.
- Vegetation type and structure: open grassland, mixed forest, shrubland, pine savanna, dense canopy.
- Moisture and hydrological setting: wet soil, marsh, floodplain, stream bank, spring seep.
- Disturbance and land use: roadside, old field, disturbed ground, burned ground, agricultural edge, power-line clearing.
- Life zones, general terrain, and microhabitats: alpine meadow, desert, rocky slopes, canyon slopes, leaf litter, tree trunks, crevices.
- All qualifying habitat phrases, including multiple habitats in the same label.

## Exclude

- Place names, named geographic features, named roads or trails, and phrases describing proximity to them.
- Distances, geographic bearings, route directions, coordinates, township/range/section references, and elevation.
- Associated taxa and host identities; these belong in `associatedTaxa`. General vegetation types such as “pine forest” remain habitat.
- Specimen traits, including height, color, flowers, fruits, developmental stage, abundance, and chromosome counts.
- Collection methods, equipment, and climate measurements.

## Mixed text: extract phrases, not whole sentences

1. Evaluate each phrase independently. A raw text sentence can contain both habitat and locality.
2. Retain the independently meaningful habitat wording and remove the locality wording, even when they occur in the same sentence.
3. Do not keep locality to make the sentence complete. A short habitat phrase is acceptable; a dangling preposition or conjunction is not.
4. Do not turn a place name into a habitat description. For example, “near McGee Creek” does not justify “creek”, “stream bank”, or “riparian habitat”.
5. Exclude proper names of fires or burns as well. Retain separately stated environmental descriptions such as “burned ground”.
6. If removing locality or other excluded information leaves no meaningful habitat phrase, return an empty string.

## Verbatim extraction

- Do not add, infer, paraphrase, summarize, or categorize information.
- Preserve the original wording, spelling, capitalization, abbreviations, and phrase order. Do not convert to sentence case.
- Each retained phrase must be copied from the source. Do not construct a new phrase by deleting words from inside a name or reference.
- Trim whitespace and dangling punctuation at extraction boundaries. When separate habitat phrases remain, join them with “; ”. This separator is the only new text allowed.
- Do not retain unintelligible text or isolated fragments that do not independently describe habitat.
- If no explicit habitat information is present, set `habitat` to `""`.

## Examples

Input: “Dry sandy soil near McGee Creek”  
habitat: “Dry sandy soil”

Input: “Near McGee Creek”  
habitat: ""

Input: “Along roadside near Mono Co. border”  
habitat: “Along roadside”

Input: “Along Highway 395”  
habitat: ""

Input: “On canyon slopes above Glen Alpine”  
habitat: “On canyon slopes”

Input: “On north-facing rocky slopes, 3 miles west of Jacumba”  
habitat: “On north-facing rocky slopes”

Input: “Near the bridge, 2 km upstream from the road junction”  
habitat: ""

Input: “Growing in moist soil with Carex obnupta”  
habitat: “Growing in moist soil”

Input: “Burned ground within the Carr Fire perimeter”  
habitat: “Burned ground”

Input: “Dry sand; near McGee Creek; open grassland; small annual with red flowers”  
habitat: “Dry sand; open grassland”