---
title: 'BifacialSimu: Hollistic Simulation of large-scale Bifacial Photovoltaic Systems'
tags:
  - Python
  - Bifacial Photovoltaic
  - Albedo
  - Simulation

authors:
  - name: Eva-Maria Grommes^[corresponding author]
    orcid: 0000-0002-7826-3754
    affiliation: 1
  - name: Sarah Glaubitz^[co-first author]
    affiliation: 2
  - name: Ulf Blieske^[co-first author]
    affiliation: 1
affiliations:
 - name: Cologne Institute for Renewable Energy (CIRE), University of Applied Science Cologne, Cologne, Germany
   index: 1
 - name: Independent Researcher
   index: 2
date: 22 April 2022
bibliography: paper.bib
---

# Summary

Due to the ongoing anthropogenic climate change and a global effort to switch energy production from fossil sources to renewable energies, bifacial photovoltaic (PV) markets are recently growing  [@Fischer.April2021]. In this context, the consideration of bifacial PV in simulation programs is gaining importance in research and engineering sectors. Bifacial PV can absorb solar radiation arriving on the front side as well as on the rear side of a PV module and use it to generate electricity, which increases the overall efficiency and the energy yield of the PV module on the same area compared to monofacial PV. Because of the significant impact of the rear side irradiance on energy yield in bifacial PV, the inclusion of exact albedo simulation, which indicates the light reflectivity of a surface, usually the ground, is indispensable. The bifacial simulation program BifacialSimu, developed at the University of Applied Sciences Cologne (Germany) and programmed in python, calculates the energy yield of a bifacial PV system based on a variety of simulation models, which the user is able to select. Moreover, it offers the option to use a constant, time-variable [@Chiodetti.June2016] or geometric spectral albedo [@Ziar.2019] to calculate the light reflectivity of the ground surface. The energy yield can be calculated using two different electrical models [@electrical_characterization].

# Statement of need

Current forecasts expect PV to be the third largest power generation technology by 2050 and will play a significant role in future global electricity generation [@InternationalRenewableEnergyAgengy.2019]. Since the specific yield of a PV-system can be increased with respect to monofacial PV, bifacial PV has become the focus of research within the last decades [@Cuavas.juni2005]. With the rapidly growing market for bifacial PV, there is also a demand for precise simulation programs for this technology to enable planners and investors to receive accurate energy yield forecasts. In recent years, more and more simulation programs and models have been published that allow the simulation of bifacial PV systems [@Stein.April2021]. In contrast to the simulation of monofacial PV, the simulation of bifacial PV is more complex since several factors are added for the energy yield prediction due to the rear side radiation. In addition to the bifaciality and the geometry of the photovoltaic field, these factors include the ground albedo, which indicates the light reflectivity of the ground. There is a need for an open source software tool to simulate bifacial PV, which combines existing radiation, new albedo and new electrical models and also provides a graphical user interface (GUI) to involve every potential user group. BifacialSimu gives the oportunity to choose between various model options for each simulation step and is well documented. Especially advanced albedo models are necessary to simulate in regions, where no measurements are possible.  BifacialSimu has already been applied in two publications [@performance_estimation_bifacial_PV,@albedo_uncertainty_Grommes], three publications regarding the validation were submitted to the World Conference on Photovoltaics Energy Conversion (WCPEC-8) and one publication was submitted to the 17th Conference on Sustainable Development of Energy, Water and Environment Systems (SDEWES) in 2022.


# State of the field

In contrast to other bifacial simulation software, BifacialSimu is the only open-source one, which combines the two radiation models viewfactor for the front side and raytracing for the rear side, which leads to the most accurate forecast [@Berrian.October2017]. Only the paid software MoBiDiG hybrid from International Solar Energy Research Center Konstanz also offers a combination of both radiation models [@Berrian.October2017]. SAM by National Renewable Energy Laboratory (NREL) does not include the option to choose between different models for electrial and albedo calculation [@SAM_NREL]. The radiation models in BifacialSimu are based on existing, open-source software. Bifacial_radiance from the NREL is used for raytracing [@Deline.2017]. This makes a full simulation of a bifacial PV system more complex and time-consuming. The commonly known open-source software using the viewfactor model, pvfactors [@Anoma.2017] and bifacialVF [@Marion.2017], have both no energy yield calculation and no GUI, which limits the target audience and the application possibilities. The commonly used software PVsyst offers an energy yield calculation and a GUI, but the used physical models are only documented to a limited extent and the software must be paid [@PVsystSA]. Besides BifacialSimu, a software including the choice between different albedo, radiation and electrial yield models is not available to the best knowledge of the authors.

# Acknowledgements
A special thanks to all the students of the University of Applied Sciences Cologne who have contributed so far to this project, it would not have been as successful without their input.

# References
