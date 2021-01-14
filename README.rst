# On indefinite hiatus

I don't promise anything, I picked this up because I like the program.
Right now I'm trying to type hint the codebase while refactoring, there
will be messy commits because I have no idea how to contribute properly.

Using PyCharm and Python 3.8.

   Follow original creator on twitter to keep up to date with HPX:

   .. image:: https://img.shields.io/twitter/follow/pewspew.svg?style=social&label=Follow
     :target: https://twitter.com/twiddly_

This is a cross platform manga/doujinshi manager with namespace & tag
support.

Features
========

-  Portable, self-contained in folder and cross-platform
-  Low memory footprint
-  Advanced gallery search with regex support (`learn more about it
   here <https://github.com/Pewpews/happypanda/wiki/Gallery-Searching>`__)
-  Gallery tagging: userdefined namespaces and tags
-  Gallery metadata fetching from the web (supports various sources)
-  Gallery downloading from the web (supports various sources) \*
-  Folder monitoring that'll notify you of filesystem changes
-  Multiple ways of adding galleries to make it as convienient as
   possible!
-  Recursive directory/archive scanning
-  Supports ZIP/CBZ, RAR/CBR and directories with loose files
-  Very customizable
-  And lots more...

\* Gallery downloading from E-Hentai costs Credits/GP

Screenshots
===========
.. image:: https://github.com/rabaarabaa/happypanda/raw/master/misc/screenshot1.png
    :width: 100%
    :align: center
.. image:: https://github.com/rabaarabaa/happypanda/raw/master/misc/screenshot2.png
    :width: 100%
    :align: center
.. image:: https://github.com/rabaarabaa/happypanda/raw/master/misc/screenshot3.png
    :width: 100%
    :align: center

How to install and run
======================

Windows
^^^^^^^

#. Download the archive from
   `releases <https://github.com/rabaarabaa/happypanda/releases>`__
#. Extract the archive to its own folder
#. Find Happypanda.exe and double click on it!

Mac and Linux
^^^^^^^^^^^^^

Install from PYPI or see `INSTALL.md <https://github.com/Pewpews/rabaarabaa/blob/master/INSTALL.md>`__

PYPI
^^^^^^^^^^^^^
``pip install happypanda`` (thanks `@Evolution0 <https://github.com/Evolution0>`__)
and then run with ``happypanda --home``

Note: use of the ``--home`` flag will make happypanda create required files and directories at:

On windows:
``'C:\Users\YourName\AppData\Local\Pewpew\Happypanda'``

On mac:
``'/Users/YourName/Library/Application Support/Happypanda'``

On linux:
``'/home/YourName/.local/share/Happypanda'``


Updating
========

| Overwrite your previous installation.
| More info in the `wiki <https://github.com/rabaarabaa/happypanda/wiki>`__


PYPI
^^^^^^^^^^^^^
``pip install --upgrade happypanda``


Misc.
=====

For general documentation (how to add galleries and usage of the
search), check the
`wiki <https://github.com/rabaarabaa/happypanda/wiki>`__.

People wanting to import galleries from the Pururin database torrent
should find `this <https://github.com/Exedge/Convertor>`__ useful.

Dependencies
============

-  Qt5 (Install this first) >= 5.4
-  PyQt5 (pip)
-  requests (pip)
-  beautifulsoup4 (pip)
-  watchdog (pip)
-  scandir (pip)
-  rarfile (pip)
-  robobrowser (pip)
-  Send2Trash (pip)
-  Pillow (pip) or PIL
-  python-dateutil (pip)
-  QtAwesome (pip)
-  appdirs (pip)

Contributing
============

You may make a pull request I guess...
