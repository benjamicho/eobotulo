﻿License: This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at your
option) any later version. This program is distributed in the hope that it
will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
---------------------------------------------------------------------------
© 2012 Thomas James
Modifications © 2013 Benjamin Krause
---------------------------------------------------------------------------

Saluton!

Agordo estas en config.py. Necesas en tiu dosiero specifi konekto-detalojn al
irc-servilo. ĉefa dosiero enhavanta main() nomiĝas eobotd.

Necesas komenci eobot kun root-privilegioj, do 'sudo ./eobotd' aŭ simile. La
demono forlasas root-privilegiojn post komenciĝo kaj funkcias sub la uznomo
specifita en la ŝlosilo 'run_as' en config.py. Necesas krei konton sub kiu
eobot povas funkcii.