# Empirical records and scope

The archive preserves published class stocks, full-precision printed areas, means, intervals, display rules, and the measurement evidence described in the original sources. It does not include the original classified numerical raster, operational class lookup, aggregation workbook, compartment-wise global carbon-fraction weights, or a representative class-5 structural survey. The available records do not establish whether those originals were lost, retained elsewhere, or superseded.

## Forward stand-structure test

Class 5 is the published 285.03 PgC / 531,449,420.52 ha component. A positive test requires independent measured stem counts, basal areas, heights, solid woody volumes, tissue density and carbon fractions, explicit remainder pools, acquisition uncertainty, and representative sampling weights on the same map epoch and class area basis. `data/stand_measurement_schema.json` defines input records; it contains no invented observations.

`python scripts/physical_closure.py --measurements measured.json --output measured_closure.json` reconstructs plot-level carbon from supplied disjoint compartments. Its structural identity is a consistency check. Independent agreement with a map and representative class-level inference require external measurement and sampling evidence. The script does not infer a typical stand from a carbon target.

Direct interval membership resolves the two intermediate printed class assignments; enumeration remains a regression check. That result does not alone choose which historical raster legend or vegetation-description assignment should be changed. Both published values and proposed label assignment remain distinguishable.

The common normalization admits an approximately 0.994% area-denominator difference as one possible mechanism. No original projection, geodesic/pixel-area weighting or resampling operation has been identified.

This edition supplies the published-data and analytical records in its companion author package. See DEPOSIT_STATUS.md for actual publication status. No private project or client documents are distributed.

## Córdoba empirical-input audit

The accessible Table 170 aggregates provide real reported basal areas, height ranges, stem densities and allometry-based biomass with measured carbon fractions. The archive transcribes the Acalypha–Guazuma community, printed page 942. Independent sound organ volumes, paired volume/material properties, individual georeferences and matched map values were not recovered. A real independent geometric residual cannot be computed from those aggregates alone and is explicitly null in the audit output. No reason for absence of the original records is inferred.

Higuchi et al. (1998), Table 3(b), was inspected in the primary-paper full text: the dry-mass means, not the separate fresh-weight percentage row, determine the 1.05% leaf fraction. The example has 38 harvested trees in the nutrient subset. Gómez González et al. (2017) separates live epiphytes from dead material and uses regression-assisted stand extrapolation. These are evidence about documented populations, not universal biological ceilings.

## Additional provenance resolved in revision 7.1

Original arXiv preprint page 23 explicitly gives a regional response range of 0–523 MgC/ha; its nominal map epoch remains 2007–2008. The mean 177.03 is not a response ceiling. A per-tree acquisition-route breakdown and the original matched voxel-convergence series have not been recovered. The companion capture schema is empty rather than filled with inferred capture modalities. New calibrations described as in development by the author have no numerical result or public map identifier in this archive.

Disney-related primary references describe structural reconstruction, the Wytham temperate example, and TLS2trees implementation benchmarks. They are evidence of the measurement route and processing requirements, not validation of the initial pantropical number. GCB atmospheric uncertainties are taken from the detailed, period-specific sections; a differing executive-summary annual value is recorded explicitly.

## Structural-envelope comparison

The 7.3 author revision compares published crown-allocation distributions and methods with explicitly specified form-factor scenarios. It does not claim that the original 51-tree or 673-tree data were newly processed, nor that a representative class-5 structural survey or its joint upper envelope was recovered. Goodman’s Dryad archive and Momo Takoudjou’s reconstruction data remain distinct primary empirical resources; their mention is not a claim to have downloaded or analysed their records.
