# BifacialSimu


BifacialSimu contains a series of python wrapper functions to simulate the energy density of a bifacial PV system. It is using libaries such as [bifacial_radiance](https://github.com/NREL/bifacial_radiance) (Ray Traying) and [pvfactors](https://github.com/SunPower/pvfactors) (View Factors).

<img src="docs/Logo/logo_BifacialSimu_transparent.png" width="500">

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Which prerequisites you need to install the software and how to install them

```
from IPython import get_ipython
get_ipython().magic('reset -sf')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
import math
import pvlib
from datetime import datetime
from pvfactors.viewfactors.aoimethods 
from pvfactors.engine import PVEngine
from pvfactors.irradiance import HybridPerezOrdered
from pvfactors.geometry import OrderedPVArray
from pvfactors.viewfactors import VFCalculator
from tqdm import tqdm
```

Additionally this video shows how to install the bifacial_radiance software and all associated software needed:
https://youtu.be/4A9GocfHKyM
```
pip install bifacial_radiance
```
If you want to make changes to the system, clone the repository, navigate to the folder and istall it in conda unsing:
```
pip install -e .
```


### Installing

A step by step series of examples that tell you how to get BifacialSimu running.

The first step to run bifacial_radiance is:

```

Copy gencumulativesky.exe from the repo’s /bifacial_radiance/data/ directory and copy into your Radiance install directory. This is typically found in /program files/radiance/bin/.

```

And repeat

```
until finished
```

Following an example with test parameters is shown.

## Running the tests

Explain how to run the automated tests for BifacialSimu

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```



## Contributing

Thank you to all the contributors to BifacialSimu, who worked on the library during their projects and thesis:

Felix Schemann, Frederik Klag, Jan Schmitt, Sarah Glaubitz, Sebastian Nows,

## Versioning

The current version is v1.

## Authors

* **Eva-Maria Grommes** - *Initial work* - [EwaGomez](https://github.com/EwaGomez)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Citing
If you use BifacialSimu in a published work, please cite:
XXXXXX


## Acknowledgments

This open-source simulation tool for bifacial PV systems is part of my PhD project at the University of Applied Sciences Cologne (Germany) and the University of Luxembourg.

