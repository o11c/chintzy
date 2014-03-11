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
OBJECTS := $(patsubst src/%.cpp,obj/%.o,${SOURCES})
BINS := main

bins: ${BINS}
objects: ${OBJECTS}

%: obj/%.o
	${CXX} ${LDFLAGS} $^ ${LDLIBS} -o $@
obj/%.o: src/%.cpp | obj/.
	${CXX} ${CPPFLAGS} ${CXXFLAGS} -c -o $@ $<
obj/.:
	mkdir obj

main: ${OBJECTS}

clean:
	rm -rf obj ${BINS}
