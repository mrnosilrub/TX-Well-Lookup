# Ground Truth Schema — ground_truth

Generated at 2025-08-17 01:14:59Z

Tables: 18

## Tables
- PlugBoreHole (approx rows: 205897)
- PlugCasing (approx rows: 121517)
- PlugData (approx rows: 240874)
- PlugRange (approx rows: 392952)
- WellBoreHole (approx rows: 808660)
- WellCasing (approx rows: 1390306)
- WellCompletion (approx rows: 712797)
- WellData (approx rows: 680955)
- WellDrillingMethod (approx rows: 695268)
- WellFilter (approx rows: 309849)
- WellInjuriousConstituent (approx rows: 7303)
- WellLevels (approx rows: 372444)
- WellLithology (approx rows: 5117189)
- WellPackers (approx rows: 313502)
- WellPlugBack (approx rows: 141957)
- WellSealRange (approx rows: 935185)
- WellStrata (approx rows: 249991)
- WellTest (approx rows: 350302)

## PlugBoreHole

Approx rows: 205897

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| PluggingReportTrackingNumber | text | YES |  |
| Diameter | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |

## PlugCasing

Approx rows: 121517

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| PluggingReportTrackingNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| Diameter | text | YES |  |

## PlugData

Approx rows: 240874

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| PluggingReportTrackingNumber | text | YES |  |
| DateSubmitted | text | YES |  |
| OwnerName | text | YES |  |
| OwnerAddress1 | text | YES |  |
| OwnerAddress2 | text | YES |  |
| OwnerCity | text | YES |  |
| OwnerState | text | YES |  |
| OwnerZip | text | YES |  |
| OwnerOtherCountry | text | YES |  |
| OwnerCountry | text | YES |  |
| OwnerWellNumber | text | YES |  |
| County | text | YES |  |
| WellAddress1 | text | YES |  |
| WellAddr2 | text | YES |  |
| WellCity | text | YES |  |
| WellZip | text | YES |  |
| WellLocationDescription | text | YES |  |
| NumberOfWellsPlugged | text | YES |  |
| Elevation | text | YES |  |
| CoordDDLat | text | YES |  |
| Dlat | text | YES |  |
| Mlat | text | YES |  |
| Slat | text | YES |  |
| CoordDDLong | text | YES |  |
| Dlong | text | YES |  |
| Mlong | text | YES |  |
| Slong | text | YES |  |
| HorizontalDatumType | text | YES |  |
| GridNumber | text | YES |  |
| LocationVerifiedByDriller | text | YES |  |
| OriginalCompanyName | text | YES |  |
| OriginalDrillerName | text | YES |  |
| OriginalLicenseNumber | text | YES |  |
| OriginalWellUse | text | YES |  |
| OriginalWellUseOtherDesc | text | YES |  |
| OriginalDrillDate | text | YES |  |
| PluggingMethod | text | YES |  |
| PluggingMethodOtherDesc | text | YES |  |
| PluggingDate | text | YES |  |
| VarianceNumber | text | YES |  |
| CompanyName | text | YES |  |
| PluggerName | text | YES |  |
| DrillerAddress1 | text | YES |  |
| DrillerAddress2 | text | YES |  |
| DrillerCity | text | YES |  |
| DrillerState | text | YES |  |
| DrillerZip | text | YES |  |
| DrillerOtherCountry | text | YES |  |
| DrillerCountry | text | YES |  |
| LicenseNumber | text | YES |  |
| DrillerSigned | text | YES |  |
| ApprenticeSigned | text | YES |  |
| ApprenticeRegistrationNumber | text | YES |  |
| Comments | text | YES |  |
| WellReportTrackingNumber | text | YES |  |

## PlugRange

Approx rows: 392952

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| PluggingReportTrackingNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| PlugSeal | text | YES |  |
| Amount | text | YES |  |
| Unit | text | YES |  |

## WellBoreHole

Approx rows: 808660

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| Diameter | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |

## WellCasing

Approx rows: 1390306

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| MigratedSortNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| MigratedCasingInfo | text | YES |  |
| Diameter | text | YES |  |
| CasingStatus | text | YES |  |
| CasingMaterial | text | YES |  |
| CasingMaterialOtherDesc | text | YES |  |
| CasingType | text | YES |  |
| CasingTypeOtherDesc | text | YES |  |
| Schedule | text | YES |  |
| Gauge | text | YES |  |

## WellCompletion

Approx rows: 712797

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| BoreholeCompletion | text | YES |  |
| BoreholeCompletionOtherDesc | text | YES |  |

## WellData

Approx rows: 680955

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| DateSubmitted | text | YES |  |
| OwnerName | text | YES |  |
| OwnerAddress1 | text | YES |  |
| OwnerAddress2 | text | YES |  |
| OwnerCity | text | YES |  |
| OwnerState | text | YES |  |
| OwnerZip | text | YES |  |
| OwnerOtherCountry | text | YES |  |
| OwnerCountry | text | YES |  |
| OwnerWellNumber | text | YES |  |
| County | text | YES |  |
| WellAddress1 | text | YES |  |
| WellAddress2 | text | YES |  |
| WellCity | text | YES |  |
| WellZip | text | YES |  |
| WellLocationDescription | text | YES |  |
| NumberOfWellsDrilled | text | YES |  |
| Elevation | text | YES |  |
| CoordDDLat | text | YES |  |
| Dlat | text | YES |  |
| Mlat | text | YES |  |
| Slat | text | YES |  |
| CoordDDLong | text | YES |  |
| Dlong | text | YES |  |
| Mlong | text | YES |  |
| Slong | text | YES |  |
| GridNumber | text | YES |  |
| LocationVerifiedByDriller | text | YES |  |
| TypeOfWork | text | YES |  |
| TypeOfWorkOtherDesc | text | YES |  |
| OriginalWellReportTrackingNumber | text | YES |  |
| ProposedUse | text | YES |  |
| ProposedUseOtherDesc | text | YES |  |
| TCEQApprovedPlans | text | YES |  |
| PWSNo | text | YES |  |
| DrillingStartDate | text | YES |  |
| DrillingEndDate | text | YES |  |
| SealMethod | text | YES |  |
| SealMethodOtherDesc | text | YES |  |
| DistanceToSepticOrOtherContamination | text | YES |  |
| DistanceToSepticTank | text | YES |  |
| DistanceToPropertyLine | text | YES |  |
| DistanceVerificationMethod | text | YES |  |
| ApprovedByVariance | text | YES |  |
| SealedByDriller | text | YES |  |
| SealedByName | text | YES |  |
| SurfaceCompletion | text | YES |  |
| SurfaceCompletionOtherDesc | text | YES |  |
| CompletedByDriller | text | YES |  |
| PumpType | text | YES |  |
| PumpTypeOtherDesc | text | YES |  |
| PumpDepth | text | YES |  |
| ChemicalAnalysis | text | YES |  |
| InjuriousWater | text | YES |  |
| CompanyName | text | YES |  |
| DrillerName | text | YES |  |
| DrillerSigned | text | YES |  |
| ApprenticeSigned | text | YES |  |
| Comments | text | YES |  |
| PluggedWithin48Hrs | text | YES |  |
| PluggingReportTrackingNumber | text | YES |  |
| KnownLocationError | text | YES |  |
| HorizontalDatumType | text | YES |  |
| DrillerAddress1 | text | YES |  |
| DrillerAddress2 | text | YES |  |
| DrillerCity | text | YES |  |
| DrillerState | text | YES |  |
| DrillerZip | text | YES |  |
| DrillerOtherCountry | text | YES |  |
| DrillerCountry | text | YES |  |
| LicenseNumber | text | YES |  |
| ApprenticeRegistrationNumber | text | YES |  |

## WellDrillingMethod

Approx rows: 695268

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| DrillingMethod | text | YES |  |
| DrillingMethodOtherDesc | text | YES |  |

## WellFilter

Approx rows: 309849

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| FilterMaterial | text | YES |  |
| FilterMaterialOtherDesc | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| Size | text | YES |  |

## WellInjuriousConstituent

Approx rows: 7303

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| NaturalInjuriousConstituent | text | YES |  |
| NaturalInjuriousConstituentOtherDesc | text | YES |  |
| UnNaturalInjuriousConstituent | text | YES |  |
| UnNaturalInjuriousConstituentOtherDesc | text | YES |  |

## WellLevels

Approx rows: 372444

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| Measurement | text | YES |  |
| MeasurementDate | text | YES |  |
| ArtesianFlow | text | YES |  |
| MeasurementMethod | text | YES |  |
| MeasurementMethodOtherDesc | text | YES |  |

## WellLithology

Approx rows: 5117189

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| MigratedSortNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| LithologyDescription | text | YES |  |

## WellPackers

Approx rows: 313502

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| MigratedSortNumber | text | YES |  |
| Packers | text | YES |  |
| PackersOtherDesc | text | YES |  |
| Depth | text | YES |  |

## WellPlugBack

Approx rows: 141957

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| MigratedSortNumber | text | YES |  |
| PlugBack | text | YES |  |
| PlugBackOtherDesc | text | YES |  |

## WellSealRange

Approx rows: 935185

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| AnnularSeal | text | YES |  |
| Amount | text | YES |  |
| Unit | text | YES |  |

## WellStrata

Approx rows: 249991

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| MigratedStrataDepth | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| WaterType | text | YES |  |

## WellTest

Approx rows: 350302

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| WellReportTrackingNumber | text | YES |  |
| TestType | text | YES |  |
| TestTypeOtherDesc | text | YES |  |
| Yield | text | YES |  |
| Drawdown | text | YES |  |
| Hours | text | YES |  |
