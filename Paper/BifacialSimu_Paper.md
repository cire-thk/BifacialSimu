---
title: 'BifacialSimu: Simulating bifacial photovoltaic systems'
tags:
  - Python
  - Bifacial Photovoltaic
  - Albedo
  - Simulation
  - # weitere tags?
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

#clear description of the high-level functionality and purpose of the software for a diverse, non-specialist audience

Due to the ongoing anthropogenic climate change and a global effort to switch energy production from fossil sources to renewable energies, bifacial photovoltaic (PV) markets are recently growing \cite{ITRPV_2020}. In this context, the consideration of bifacial PV in simulation programs is gaining importance in research and engineering sectors. Bifacial PV can absorb solar radiation arriving on the front side as well as on the rear side of a PV module and use it to generate electricity, which increases the overall efficiency and the energy yield of the PV module on the same area compared to monofacial PV. Because of the significant impact of the rear side irradiance on energy yield in bifacial PV, the inclusion of albedo, which indicates the light reflectivity of a surface, usually the ground, is indispensable. The bifacial simulation program BifacialSimu, developed at the University of Applied Sciences Cologne (Germany) and programmed in python, calculates the energy yield of a bifacial PV system based on two different radiation simulations – view factor \cite{VF_validation} and raytracing \cite{model_validation}. Moreover, it offers the option to use a constant, time-variable or geometric spectral albedo \cite{impact_spectral_albedo_dataset} to calculate the light reflectivity of the ground surface. , The energy yield can be calculated using two different electrical models \cite{electrical_characterization}.

#viewfactor, raytracing constant, time-variable und spectral albedo jeweils kurz erläutern?
#Ich glaube es reicht, wenn wir die jeweiligen Paper mal zitieren! Das Beispielpaper auf der Homepage des Journals ist ja recht kurz.


# Statement of need

#problems the software is designed to solve
#the target audience

Photovoltaic (PV) is the second largest power generation technology and will play a significant role in future global electricity generation [reference]. Since the efficiency of a monofacial silicon PV cell is physically limited to 29.4 % [MA Sarah, reference 5], bifacial PV has become the focus of research within the last decades [MA Sarah, reference 6]. With the rapidly growing market for bifacial PV, there is also a demand for precise simulation programs for this technology to enable planners and investors accurate energy yield forecasts. In recent years, more and more simulation programs and models have been published that allow the simulation of bifacial PV systems [MA Sarah, reference 10, p. 82]. In contrast to the simulation of monofacial PV, the simulation of bifacial PV is more complex since several factors are added for the energy yield prediction due to the rear side radiation. In addition to the bifaciality and the geometry of the photovoltaic field, these factors include the ground albedo, which indicates the light reflectivity of the ground. There is a need for an open source software tool to simulate bifacial PV, which combines existing radiation and electrical models and provides a graphical user interface (GUI). The GUI makes the software available to a wider audience, f.e. students or researcher with low python knowledge.

#SG: ich bin mir nicht sicher ob wir in dem Kapitel PV als Abkürzung nochmal neu einführen müssen. Da dieses paper im Vergleich zu anderen sehr kurz gehalten ist und die summary ergänzend zu dem Kapitel ist, würde ich sagen eher nicht

# State of the field

#how this software compares to other commonly-used packages

#Ideen: Direkter Vergleich in den Eigenschaften zu VF, RT und PVSyst. VF hat keine GUI, RT hat keine elektrischen Berechnungen, PVSyst ist teuer und nicht nachvollziehbar welche Modelle verwendet wurden.
#SG: finde die Ideen gut und passend, werde dazu was ausformulieren


# Acknowledgements
A special thanks to all the students who have contributed so far to this project, it wouldn't have been as successful without their input.

#SG: Students im Acknowledgements spezifizieren? students of the University of Applied Science Cologne

# References
#Ich habe jetzt die LaTeX Zitierweise genutzt, bin mir aber nicht sicher, ob das richtig ist. wie verstehst du die Seite hier? https://pandoc.org/MANUAL.html#citations
#SG: ich gucke mir die Citations Vorgaben am WE an, hatte die Wibsite auch schon gesehen, aber bin noch nicht drauf eingegangen. Dann ergänze ich auch noch meine MA Quellen in der bib Datei
