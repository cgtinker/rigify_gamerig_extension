Welcome to Rigify Gamerig Extension's documentation!
====================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The add-on is supposed to extend rigify with a simple goal:
Mirrow the animations of the generated rigs back to their meta-rigs.

Why?
    Game engines usually face issues with the generated rigify rig due to bendy bones
    and the mix of control and deform layer. The meta-rig however, suits most game engines
    very well and if modifications are necessary it's usually not a huge effort.
    This add-ons purpose is to help animators to mirrow animations from the generated rig to the meta-rig.

.. warning::
   This add-on is supposed to be used to improve the export to game-engines.
   When doing so, ensure to bind the character to the meta-rig, to use the meta-rig as deform rig.
   It may not be of any use, when you are planning to animate strictly within Blender.


Contents
--------

.. toctree::
   installation
   usage
