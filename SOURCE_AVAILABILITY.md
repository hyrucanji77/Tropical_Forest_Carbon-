# Empirical records and scope

The archive preserves published class stocks, full-precision printed areas, means, intervals, display rules, and the measurement evidence described in the original sources. It does not include the original classified numerical raster, operational class lookup, aggregation workbook, compartment-wise global carbon-fraction weights, or a representative class-5 structural survey. The available records do not establish whether those originals were lost, retained elsewhere, or superseded.

## Forward stand-structure test

Class 5 is the published 285.03 PgC / 531,449,420.52 ha component. A positive test requires independent measured stem counts, basal areas, heights, solid woody volumes, tissue density and carbon fractions, explicit remainder pools, acquisition uncertainty, and representative sampling weights on the same map epoch and class area basis. `data/stand_measurement_schema.json` defines input records; it contains no invented observations.

`python scripts/physical_closure.py --measurements measured.json --output measured_closure.json` reconstructs plot-level carbon from supplied disjoint compartments. Its structural identity is a consistency check. Independent agreement with a map and representative class-level inference require external measurement and sampling evidence. The script does not infer a typical stand from a carbon target.

The tabular relabelling is unique among the 120 permutations of fixed source intervals and intact numerical rows. That result does not alone choose which historical raster legend or vegetation-description assignment should be changed. Both published values and proposed label assignment remain distinguishable.

The common normalization admits an approximately 0.994% area-denominator difference as one possible mechanism. No original projection, geodesic/pixel-area weighting or resampling operation has been identified.

This frozen research archive is identified by GitHub release v6.5. No private project or client documents are distributed.

## Córdoba empirical-input audit

The accessible Table 170 aggregates provide real reported basal areas, height ranges, stem densities and allometry-based biomass with measured carbon fractions. The archive transcribes the Acalypha–Guazuma community, printed page 942. Independent sound organ volumes, paired volume/material properties, individual georeferences and matched map values were not recovered. A real independent geometric residual cannot be computed from those aggregates alone and is explicitly null in the audit output. No reason for absence of the original records is inferred.

Higuchi et al. (1998), Table 3(b), was inspected in the primary-paper full text: the dry-mass means, not the separate fresh-weight percentage row, determine the 1.05% leaf fraction. The example has 38 harvested trees in the nutrient subset. Gómez González et al. (2017) separates live epiphytes from dead material and uses regression-assisted stand extrapolation. These are evidence about documented populations, not universal biological ceilings.
