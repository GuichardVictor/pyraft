define color
	if test -n "${TERM}" ; then\
	if test `tput colors` -gt 0 ; then\
		tput setaf $(1); \
		fi;\
	fi
endef

define default_color
	if test -n "${TERM}" ; then\
	if test `tput colors` -gt 0 ; then tput sgr0 ; fi;\
	fi
endef

all: post-build

pre-build:
	@$(call color,4)
	@echo "--> Installing dependencies <--"
	@$(call default_color)

post-build:
	@make --no-print-directory requirements ; \
	sta=$$? ; \
	$(call color,4) ; \
	echo "--> Please use start.sh to run the program <--" ; \
	$(call default_color); \
	exit $$sta;

requirements: pre-build install

install:
	pip3 install -r requirements.txt

clean:
	rm -f client_log_?.log
	rm hostfile

.PHONY: all clean install requirements pre-build post-build