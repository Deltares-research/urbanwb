.. urbanwb documentation master file, created by
   sphinx-quickstart on Thu Jul  5 08:29:21 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================
Welcome to Urbanwb's |release| documentation!
=============================================
Introduction
------------
Urbanwb model is a dynamic urban water balance model initially created by Toine Vergroesen [1]_ in Excel spreadsheet in
2013 for the purpose of rapidly modelling the water system dynamics in urban environment.
The model also supports other functions, e.g. to produce Storage-Discharge-Frequency (SDF) Curve and
to test the effectiveness of several urban adaptation measures.
It has since been successfully applied in multiple projects around the world.
Through years of evolution, the model has continuously grown to be increasingly complex,
and Excel spreadsheet no longer suits the extensibility requirement.
Hence in 2018, the model is reprogrammed from scratch into an open source Python-based package by Wenxing Zhang [2]_ and Martijn Visser [3]_.
Compared to the original Excel-version model, the Python-based Urbanwb model is easier to understand, implement, adapt and extend.
Urbanwb is a work in progress, input is welcome. The available documentation is limited for now.

.. note::
   The Urbanwb is distributed under `MIT license <https://opensource.org/licenses/MIT>`_.
   This documentation generated on |today| is for release |release| of Urbanwb model.

   Latest release (stable) version documentation:

   http://urbanwb.readthedocs.org/en/stable/  https://wxzhang.gitlab.io/UWM/

   Source code: https://gitlab.com/wxzhang/UWM

Installation
============
.. toctree::
   :maxdepth: 2

   installation

Model overview
==============
.. toctree::
   :maxdepth: 2

   urbanwb_overview

How to run a model
==================
.. toctree::
   :maxdepth: 2

   urbanwb_usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. [1] Expert hydrologist, Deltares, the Netherlands
.. [2] Msc student, TU Delft, the Netherlands
.. [3] Researcher, Deltares, the Netherlands