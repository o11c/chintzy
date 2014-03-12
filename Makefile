CXX = g++
CXXFLAGS = -g -O2
CPPFLAGS =
LDFLAGS =
LDLIBS =

# support out-of-tree builds by symlinking the makefile
BASE := $(dir $(realpath ${MAKEFILE_LIST}))
vpath %.cpp ${BASE}
vpath %.hpp ${BASE}

SOURCES := $(subst ${BASE}/,,$(wildcard ${BASE}/src/*.cpp))
HEADERS := $(subst ${BASE}/,,$(wildcard ${BASE}/src/*.hpp))
OBJECTS := $(patsubst src/%.cpp,obj/%.o,${SOURCES})
BINS := main

bins: ${BINS}
objects: ${OBJECTS}

%: obj/%.o
	${CXX} ${LDFLAGS} $^ ${LDLIBS} -o $@
obj/%.o: src/%.cpp ${HEADERS} | obj/.
	${CXX} ${CPPFLAGS} ${CXXFLAGS} -c -o $@ $<
obj/.:
	mkdir obj

override CXXFLAGS += -std=c++0x

main: ${OBJECTS}

clean:
	rm -rf obj ${BINS}
test:
	set -e; for s in ${HEADERS} ${SOURCES}; do cp $$s input; ./main; mv output $$s; done
	rm input
	rm error
	git diff --exit-code
