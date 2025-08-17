# Ground Truth Schema — gwdb_ground_truth

Generated at 2025-08-17 12:57:09Z

Tables: 16

## Tables
- WaterLevelsCombination (approx rows: 29314)
- WaterLevelsMajor (approx rows: 1577207)
- WaterLevelsMinor (approx rows: 276406)
- WaterLevelsOtherUnassigned (approx rows: 126393)
- WaterQualityCombination (approx rows: 69261)
- WaterQualityMajor (approx rows: 2227295)
- WaterQualityMinor (approx rows: 426131)
- WaterQualityOtherUnassigned (approx rows: 161419)
- WellBoreHole (approx rows: 5570)
- WellCasing (approx rows: 140264)
- WellFilter (approx rows: 1866)
- WellLithology (approx rows: 95879)
- WellMain (approx rows: 142546)
- WellPackers (approx rows: 613)
- WellSealRange (approx rows: 1965)
- WellTest (approx rows: 7826)

## WaterLevelsCombination

Approx rows: 29314

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Status | text | YES |  |
| MeasurementMonth | text | YES |  |
| MeasurementDay | text | YES |  |
| MeasurementYear | text | YES |  |
| MeasurementDate | text | YES |  |
| MeasurementTime | text | YES |  |
| DepthFromLSD | text | YES |  |
| LandElevation | text | YES |  |
| LandElevationMethod | text | YES |  |
| WaterElevation | text | YES |  |
| MeasurementNumber | text | YES |  |
| MeasuringAgency | text | YES |  |
| MethodOfMeasurement | text | YES |  |
| Remarks | text | YES |  |
| Comments | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterLevelsMajor

Approx rows: 1577207

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Status | text | YES |  |
| MeasurementMonth | text | YES |  |
| MeasurementDay | text | YES |  |
| MeasurementYear | text | YES |  |
| MeasurementDate | text | YES |  |
| MeasurementTime | text | YES |  |
| DepthFromLSD | text | YES |  |
| LandElevation | text | YES |  |
| LandElevationMethod | text | YES |  |
| WaterElevation | text | YES |  |
| MeasurementNumber | text | YES |  |
| MeasuringAgency | text | YES |  |
| MethodOfMeasurement | text | YES |  |
| Remarks | text | YES |  |
| Comments | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterLevelsMinor

Approx rows: 276406

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Status | text | YES |  |
| MeasurementMonth | text | YES |  |
| MeasurementDay | text | YES |  |
| MeasurementYear | text | YES |  |
| MeasurementDate | text | YES |  |
| MeasurementTime | text | YES |  |
| DepthFromLSD | text | YES |  |
| LandElevation | text | YES |  |
| LandElevationMethod | text | YES |  |
| WaterElevation | text | YES |  |
| MeasurementNumber | text | YES |  |
| MeasuringAgency | text | YES |  |
| MethodOfMeasurement | text | YES |  |
| Remarks | text | YES |  |
| Comments | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterLevelsOtherUnassigned

Approx rows: 126393

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Status | text | YES |  |
| MeasurementMonth | text | YES |  |
| MeasurementDay | text | YES |  |
| MeasurementYear | text | YES |  |
| MeasurementDate | text | YES |  |
| MeasurementTime | text | YES |  |
| DepthFromLSD | text | YES |  |
| LandElevation | text | YES |  |
| LandElevationMethod | text | YES |  |
| WaterElevation | text | YES |  |
| MeasurementNumber | text | YES |  |
| MeasuringAgency | text | YES |  |
| MethodOfMeasurement | text | YES |  |
| Remarks | text | YES |  |
| Comments | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterQualityCombination

Approx rows: 69261

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| SampleMonth | text | YES |  |
| SampleDay | text | YES |  |
| SampleYear | text | YES |  |
| SampleDate | text | YES |  |
| SampleTime | text | YES |  |
| SampleTimeZone | text | YES |  |
| SampleNumber | text | YES |  |
| Reliability | text | YES |  |
| CollectionEntity | text | YES |  |
| AnalyzedLab | text | YES |  |
| SampledAquifer | text | YES |  |
| SampleTopInterval | text | YES |  |
| SampleBottomInterval | text | YES |  |
| CollectionRemarks | text | YES |  |
| SampleBU | text | YES |  |
| SampleBUValue | text | YES |  |
| ParameterCode | text | YES |  |
| ParameterDescription | text | YES |  |
| ParameterUnitOfMeasure | text | YES |  |
| ParameterFlag | text | YES |  |
| ParameterValue | text | YES |  |
| ParameterValuePlusMinus | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterQualityMajor

Approx rows: 2227295

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| SampleMonth | text | YES |  |
| SampleDay | text | YES |  |
| SampleYear | text | YES |  |
| SampleDate | text | YES |  |
| SampleTime | text | YES |  |
| SampleTimeZone | text | YES |  |
| SampleNumber | text | YES |  |
| Reliability | text | YES |  |
| CollectionEntity | text | YES |  |
| AnalyzedLab | text | YES |  |
| SampledAquifer | text | YES |  |
| SampleTopInterval | text | YES |  |
| SampleBottomInterval | text | YES |  |
| CollectionRemarks | text | YES |  |
| SampleBU | text | YES |  |
| SampleBUValue | text | YES |  |
| ParameterCode | text | YES |  |
| ParameterDescription | text | YES |  |
| ParameterUnitOfMeasure | text | YES |  |
| ParameterFlag | text | YES |  |
| ParameterValue | text | YES |  |
| ParameterValuePlusMinus | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterQualityMinor

Approx rows: 426131

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| SampleMonth | text | YES |  |
| SampleDay | text | YES |  |
| SampleYear | text | YES |  |
| SampleDate | text | YES |  |
| SampleTime | text | YES |  |
| SampleTimeZone | text | YES |  |
| SampleNumber | text | YES |  |
| Reliability | text | YES |  |
| CollectionEntity | text | YES |  |
| AnalyzedLab | text | YES |  |
| SampledAquifer | text | YES |  |
| SampleTopInterval | text | YES |  |
| SampleBottomInterval | text | YES |  |
| CollectionRemarks | text | YES |  |
| SampleBU | text | YES |  |
| SampleBUValue | text | YES |  |
| ParameterCode | text | YES |  |
| ParameterDescription | text | YES |  |
| ParameterUnitOfMeasure | text | YES |  |
| ParameterFlag | text | YES |  |
| ParameterValue | text | YES |  |
| ParameterValuePlusMinus | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WaterQualityOtherUnassigned

Approx rows: 161419

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| SampleMonth | text | YES |  |
| SampleDay | text | YES |  |
| SampleYear | text | YES |  |
| SampleDate | text | YES |  |
| SampleTime | text | YES |  |
| SampleTimeZone | text | YES |  |
| SampleNumber | text | YES |  |
| Reliability | text | YES |  |
| CollectionEntity | text | YES |  |
| AnalyzedLab | text | YES |  |
| SampledAquifer | text | YES |  |
| SampleTopInterval | text | YES |  |
| SampleBottomInterval | text | YES |  |
| CollectionRemarks | text | YES |  |
| SampleBU | text | YES |  |
| SampleBUValue | text | YES |  |
| ParameterCode | text | YES |  |
| ParameterDescription | text | YES |  |
| ParameterUnitOfMeasure | text | YES |  |
| ParameterFlag | text | YES |  |
| ParameterValue | text | YES |  |
| ParameterValuePlusMinus | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellBoreHole

Approx rows: 5570

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Diameter | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellCasing

Approx rows: 140264

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Diameter | text | YES |  |
| CasingMaterial | text | YES |  |
| CasingMaterialOtherDesc | text | YES |  |
| CasingType | text | YES |  |
| CasingTypeOtherDesc | text | YES |  |
| Schedule | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| Gauge | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellFilter

Approx rows: 1866

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| FilterMaterial | text | YES |  |
| FilterMaterialOtherDesc | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| Size | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellLithology

Approx rows: 95879

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| LithologyDescription | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellMain

Approx rows: 142546

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| RiverBasin | text | YES |  |
| GMA | text | YES |  |
| RWPA | text | YES |  |
| GCD | text | YES |  |
| AquiferCode | text | YES |  |
| AquiferCodeDescription | text | YES |  |
| AquiferId | text | YES |  |
| Aquifer | text | YES |  |
| Classification | text | YES |  |
| AquiferPickMethod | text | YES |  |
| LatitudeDD | text | YES |  |
| Dlat | text | YES |  |
| Mlat | text | YES |  |
| Slat | text | YES |  |
| LongitudeDD | text | YES |  |
| Dlong | text | YES |  |
| Mlong | text | YES |  |
| Slong | text | YES |  |
| CoordinateSource | text | YES |  |
| Owner | text | YES |  |
| Driller | text | YES |  |
| WellDepth | text | YES |  |
| DepthSource | text | YES |  |
| LandSurfaceElevation | text | YES |  |
| LandSurfaceElevationMethod | text | YES |  |
| DrillingStartDate | text | YES |  |
| DrillingMonth | text | YES |  |
| DrillingDay | text | YES |  |
| DrillingYear | text | YES |  |
| DrillingEndDate | text | YES |  |
| DrillingMethod | text | YES |  |
| BoreHoleCompletion | text | YES |  |
| WellType | text | YES |  |
| Pump | text | YES |  |
| PowerType | text | YES |  |
| WellUse | text | YES |  |
| WaterLevelStatus | text | YES |  |
| CurrentWaterLevelWell | text | YES |  |
| WaterQualityAvailable | text | YES |  |
| CurrentWaterQualityWell | text | YES |  |
| ReportingAgency | text | YES |  |
| OtherDataAvailable | text | YES |  |
| Remarks | text | YES |  |
| WellReportTrackingNumber | text | YES |  |
| PluggingReportTrackingNumber | text | YES |  |
| USGSSiteNumber | text | YES |  |
| TCEQSourceId | text | YES |  |
| GCDWellNumber | text | YES |  |
| OwnerWellNumber | text | YES |  |
| OtherWellNumber | text | YES |  |
| PreviousStateWellNumber | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellPackers

Approx rows: 613

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| Packers | text | YES |  |
| PackersOtherDesc | text | YES |  |
| Depth | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellSealRange

Approx rows: 1965

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| SealMethod | text | YES |  |
| SealMethodOtherDesc | text | YES |  |
| TopDepth | text | YES |  |
| BottomDepth | text | YES |  |
| AnnularSeal | text | YES |  |
| Amount | text | YES |  |
| Unit | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |

## WellTest

Approx rows: 7826

| Column | Type | Nullable | Comment |
|---|---|:--:|---|
| StateWellNumber | text | YES |  |
| County | text | YES |  |
| Aquifer | text | YES |  |
| WellTestMonth | text | YES |  |
| WellTestDay | text | YES |  |
| WellTestYear | text | YES |  |
| WellTestDate | text | YES |  |
| TestType | text | YES |  |
| TestTypeOtherDesc | text | YES |  |
| Yield | text | YES |  |
| Drawdown | text | YES |  |
| Hours | text | YES |  |
| CreatedDate | text | YES |  |
| LastUpdateDate | text | YES |  |
