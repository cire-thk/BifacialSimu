---
title: 'BifacialSimu: Simulating bifacial photovoltaic systems'
tags:
  - Python
  - Bifacial Photovoltaic
  - Albedo
  - Simulation
  - #weitere tags?
authors:
  - name: Eva Maria Grommes^[corresponding author]
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
date: XX May 2022
bibliography: paper.bib
---

# Summary

#clear description of the high-level functionality and purpose of the software for a diverse, non-specialist audience

Due to the ongoing anthropogenic climate change and a global effort to switch energy production from fossil sources to renewable energies, bifacial photovoltaic (PV) markets are recently growing  [@Fischer.April2021]. In this context, the consideration of bifacial PV in simulation programs is gaining importance in research and engineering sectors. Bifacial PV can absorb solar radiation arriving on the front side as well as on the rear side of a PV module and use it to generate electricity, which increases the overall efficiency and the energy yield of the PV module on the same area compared to monofacial PV. Because of the significant impact of the rear side irradiance on energy yield in bifacial PV, the inclusion of albedo, which indicates the light reflectivity of a surface, usually the ground, is indispensable. The bifacial simulation program BifacialSimu, developed at the University of Applied Sciences Cologne (Germany) and programmed in python, calculates the energy yield of a bifacial PV system based on two different radiation models – view factor [@Anoma.2017] and raytracing [@Deline.2017]. Moreover, it offers the option to use a constant, time-variable [@Chiodetti.June2016] or geometric spectral albedo [@Ziar.2019] to calculate the light reflectivity of the ground surface. The energy yield can be calculated using two different electrical models [@electrical_characterization].

# Statement of need

#problems the software is designed to solve
#the target audience

PV is the third largest power generation technology and will play a significant role in future global electricity generation [@InternationalRenewableEnergyAgengy.2019]. Since the efficiency of a monofacial silicon PV cell is physically limited to 29.4 % [@Richter.2013], bifacial PV has become the focus of research within the last decades [@Cuavas.juni2005]. With the rapidly growing market for bifacial PV, there is also a demand for precise simulation programs for this technology to enable planners and investors accurate energy yield forecasts. In recent years, more and more simulation programs and models have been published that allow the simulation of bifacial PV systems [@Stein.April2021]. In contrast to the simulation of monofacial PV, the simulation of bifacial PV is more complex since several factors are added for the energy yield prediction due to the rear side radiation. In addition to the bifaciality and the geometry of the photovoltaic field, these factors include the ground albedo, which indicates the light reflectivity of the ground. There is a need for an open source software tool to simulate bifacial PV, which combines existing radiation and electrical models and provides a graphical user interface (GUI). The GUI makes the software available to a wider audience, f.e. students or researcher with low python knowledge.


# State of the field

#how this software compares to other commonly-used packages

In contrast to other bifacial simulation software, BifacialSimu is the only one, with combines the two radiation models viewfactor and raytracing and is open source. Only the paid software MoBiDiG hybrid from International Solar Energy Research Center Konstanz also offers a combination of both radiation models [@Berrian.October2017]. The radiation models are based on existing, open-source software. Bifacial_radiance from the National Renewable Energy Laboratory (NREL) is used for raytracing [@Deline.2017]. BifacialSimu offers the advantage of an integrated energy yield calculation, whereas bifacial_radiance need a third software, the open-source software PVMismatch [@Mikofski.2018]. This makes a full simulation of a bifacial PV system more complex and time-consuming. The commonly known open-source software using the viewfactor model, pvfactors [@Anoma.2017] and bifacialVF [@Marion.2017], have both no energy yield calculation and no GUI, which limits the target audience and the application possibilities. The commonly used software PVsyst offers an energy yield calculation and a GUI, but the used physical models are only documented to a limited extent and the software must be paid [@PVsystSA.].

# Acknowledgements
A special thanks to all the students of the University of Applied Sciences Cologne who have contributed so far to this project, it wouldn't have been as successful without their input.

# References
#Ich habe jetzt die LaTeX Zitierweise genutzt, bin mir aber nicht sicher, ob das richtig ist. wie verstehst du die Seite hier? https://pandoc.org/MANUAL.html#citations
#SG: ich verstehe die Zitierweise im Fließtext folgendermaßen: [@author1] Aber bin mir da nicht sicher. Guck mal hier: https://pandoc.org/MANUAL.html#extension-citations
#SG: References MA sind ergänzt und paper.bib Datei sortiert
