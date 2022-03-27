---
title: 'BifacialSimu: Simulating bifacial photovoltaic systems'
tags:
  - Python
  - Bifacial photovoltiac
  - Albedo
  - Simulation
  -
authors:
  - name: Eva Maria Grommes^[corresponding author]
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Ulf Blieske^[co-first author]
    affiliation: 1
  - name: Sarah Glaubitz^[co-first author]
    affiliation: 2
affiliations:
 - name: Cologne Institute for Renewable Energy (CIRE), University of Applied Science Cologne, Cologne, Germany
   index: 1
 - name: Independent Researcher
   index: 2
date: XX May 2022
bibliography: paper.bib
---

# Summary

#clear description of the high-level functionality and purpose of the software for a di-verse, non-specialist audience

Due to the ongoing anthropogenic climate change and a global effort to switch energy production from fossil sources to renewable energies, bifacial photovoltaic markets are recently growing. In this context, the consideration of bifacial photovoltaic in simulation programs is gaining importance in research and engineering sectors. Bifacial Photovoltaic can absorb solar radiation arriving on the front side as well as on the rear side of a photovoltaic module and use it to generate electricity, which increases the overall efficiency and the energy yield of the photovoltaic module. Because of the significant impact of the rear side irradiance on energy yield in bifacial photovoltaic, the inclusion of albedo, which indicates the light reflectivity of a surface, usually the ground, is indispensable. The bifacial simulation program BifacialSimu, developed at the University of Applied Sciences Cologne and programmed in python, calculates the energy yield of a bifacial pho-tovoltaic system based on two different radiation simulations – view factor and raytracing. Moreover, it uses a constant, time-variable or geometric spectral albedo to calculate the light reflectivity of the ground surface.
#viewfactor, raytracing constant, time-variable und spectral albedo jeweils kurz erläutern?


# Statement of need

#problems the software is designed to solve
#the target audience

Due to the ongoing anthropogenic climate change, there is a global effort to switch energy production from fossil sources to renewable energies. Photovoltaic is the second largest power generation technology and will play a significant role in future global electricity generation. Since the efficiency of a monofacial silicon PV cell is physically limited to 29.4 % [MA Sarah, reference 5], bifacial photovoltaic has become the focus of research within the last decades [MA Sarah, reference 6] and gaining growing market shares. Bifacial photovoltaic can absorb solar radiation arriving on the front side as well as on the rear side and use it to generate electricity, which increases the overall efficiency. With the rapidly growing market for bifacial photovoltaic, there is also a demand for precise simulation programs for this technology to enable planners and investors accurate energy yield forecasts. In recent years, more and more simulation programs and models have been published that allow the simulation of bifacial photovoltaic systems [MA Sarah, reference 10, p. 82]. In contrast to the simulation of monofacial photovoltaic, the simulation of bifacial photovoltaic is more complex since several factors are added for the energy yield prediction due to the rear side radiation. In addition to the bifaciality and the geometry of the photovoltaic field, these factors include the ground albedo, which indicates the light reflectivity of the ground.



# State of the field

#how this software compares to other commonly-used packages


# Acknowledgements



# References
