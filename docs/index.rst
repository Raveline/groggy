.. Groggy documentation master file, created by
   sphinx-quickstart on Sun Jan  3 16:22:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Groggy's documentation!
==================================

Groggy is a simple framework built on top of `libtcod <http://roguecentral.org/doryen/libtcod/>`_

It provides:

- A simple (not thread safe) event bus management system (groggy.events)
- An input management that plugs itself to this event bus (groggy.inputs)
- A game state abstraction (groggy.ui.state)
- A menu builder and menu components system (groggy.ui.component_builder)
- Various utilities (simple geometry, wrapping of tcod consoles, etc.) (grogy.utils and groggy.view)
- Viewport management for scrolling (groggy.viewport)
- A light-weight engine (groggy.game) that mix most of those features and handle game states

Many features are rather flawed and this should be regarded as a work-in-progress.


Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
