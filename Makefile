CC ?= cc
CFLAGS ?= -O2
PREFIX ?= /usr/local
LDFLAGS ?=
LDLIBS = -lm
VERSION := $(shell cat VERSION)
CODENAME ?= Neon Spin
PYTHON ?= python3

UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_S),Darwin)
  LDLIBS += -framework IOKit -framework CoreFoundation
endif

ffetch-3d: fetch.c VERSION
	$(CC) $(CFLAGS) $(LDFLAGS) -DFETCH_VERSION='"$(VERSION)"' -DFETCH_CODENAME='"$(CODENAME)"' -DFETCH_ARCH='"$(UNAME_M)"' -DFETCH_OS='"$(UNAME_S)"' -o $@ $< $(LDLIBS)

install: ffetch-3d
	install -d $(DESTDIR)$(PREFIX)/bin
	install -m 755 ffetch-3d $(DESTDIR)$(PREFIX)/bin/ffetch-3d
	install -m 755 scripts/neonfetch $(DESTDIR)$(PREFIX)/bin/ffetch-neon
	install -m 755 scripts/arcticfetch $(DESTDIR)$(PREFIX)/bin/ffetch-arctic
	install -d $(DESTDIR)$(PREFIX)/share/doc/ffetch-3d
	install -m 644 LICENSE README.md examples/config $(DESTDIR)$(PREFIX)/share/doc/ffetch-3d/

test: ffetch-3d
	$(PYTHON) -m unittest discover -s tests -v

clean:
	rm -f ffetch-3d

.PHONY: install clean test
