# LFSCI
LiDAR Forest Structure Change Index (LFSCI): A Simple Index for Assessing Forest Loss from Snow and Ice Storms Using Bitemporal UAV LiDAR Data.
## Overview
This repository implements the LiDAR Forest Structure Change Index (LFSCI), a metric designed to quantify forest structural changes from bitemporal UAV LiDAR data, particularly for assessing damage from snow and ice storms.

## Key Features
- **Three indicators**  
  - `LFSCI`: LiDAR forest structural change index  
  - `LFSCI_C`: Canopy structural change index (above crown initiation)  
  - `LFSCI_U`: Under‐canopy structural change index (below crown initiation)  
- **Automated vertical analysis**  
  - Crown initiation layer detection  
  - Normalized point density profiling  
  - 100‐layer vertical stratification  
- **Batch processing**  
  - Handles multiple LAS/LAZ files automatically  

## Installation

### Prerequisites
- laspy >= 2.0.0
- numpy >= 1.20.0
- tqdm >= 4.60.0

```bash
cd LFSCI
pip install -r requirements.txt
```

## Usage

### Data Preparation
Organize point clouds:
```
LFSCI/
├── point_clouds/
│   ├── T1/  # Time period 1 LAS files
│   └── T2/  # Time period 2 LAS files
└── results/ # Output directory (auto-created)
Ensure filename correspondence between T1 and T2 folders
```

### Execution
```bash
python LFSCI.py
```
Output
Results are saved as CSV with columns:

| Column   | Description                                           |
|----------|------------------------------------------------------|
| ID       | Filename base                                        |
| LFSCI    | LiDAR forest structural change index                 |
| LFSCI_C  | Canopy structural change index (above crown initiation) |
| LFSCI_U  | Under canopy structural change index (below crown initiation) |

## Technical Details
### Parameters
```
'LFSCI_layers': 100,      # Number of vertical layers
'LFSCI_min_height': 0,    # Minimum height of points included in calculation (in meters; can be used to filter ground points in sparse forests)
'crown_init_threshold': 0.2  # Growth rate threshold for identifying the crown initiation layer
```

### Interpretation Guide
| Value Range | Interpretation           |
|-------------|-------------------------|
| > 0         | growth/recovery  |
| < 0         | damage/loss      |

## Citation
Please cite:

Author, A. (Year). Paper Title. Journal, Volume(Issue), pages. DOI

## License
MIT License

## Contact
Yuanyong Dian - dianyuanyong@mail.hzau.edu.cn  
College of Horticulture and Forestry Sciences, Huazhong Agricultural University  
[GitHub Repository](https://github.com/diyoejw/LFSCI.git)

## Notes
1. Adjust file paths if using different directory structure
2. Modify parameters in the script as needed for your study area
3. Ensure LAS files are in the correct format (LAS/LAZ) and have the same projection
4. Use the `LFSCI.py` script to process all LAS files in the specified folders