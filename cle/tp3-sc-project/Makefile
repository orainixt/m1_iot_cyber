SRCS := $(wildcard *.yaml)
UMLS = $(SRCS:.yaml=.plantuml)
PNGS = $(SRCS:.yaml=.png)

view : $(PNGS)
	@xdg-open $(PNGS)

%.png : %.plantuml
	plantuml $<

%.plantuml : %.yaml
	sismic-plantuml $< > $@

clean:
	rm -rf $(UMLS)
	rm -rf $(PNGS)
	rm -rf *~
