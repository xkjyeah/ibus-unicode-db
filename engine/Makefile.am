# vim:set noet ts=4:
#_
# ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2007-2012 Peng Huang <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

engine_unicode_db_PYTHON = \
	engine.py \
	main.py \
	dataparse.py \
	$(NULL)
engine_unicode_dbdir = $(datadir)/ibus-unicode-db

libexec_SCRIPTS= ibus-engine-unicode-db

bin_SCRIPTS = ibus-engine-unicode-db

component_DATA = unicode-db-python.xml
componentdir = @IBUS_DATADIR@/ibus/component

CLEANFILES = \
	*.pyc \
	$(NULL)

EXTRA_DIST = \
	ibus-engine-unicode-db.in \
	unicode-db-python.xml.in.in \
	$(NULL)

dataparse.py: dataparse.py.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

unicode-db-python.xml: unicode-db-python.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

test:
	$(ENV) \
		LANG=en_US \
		PYTHONPATH=$(top_srcdir) \
		$(PYTHON) $(srcdir)/main.py

