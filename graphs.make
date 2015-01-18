STANDARDS = cxx14 cxx11 cxx98 c11 c99 c89
GRAMMARS = parse lex preprocessor

# Carefully ordered to put the most expensive first,
# since they take more time to render than everything else combined.
GRAPHS := $(foreach grm,${GRAMMARS},$(foreach std,${STANDARDS},${std}-${grm}))

all: $(patsubst %,data/%.png,${GRAPHS})

%.png: %.dot
	dot -Tpng $< -o $@
