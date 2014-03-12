CXX = g++
CXXFLAGS = -g -O2
CPPFLAGS =
LDFLAGS =
LDLIBS =

DIFF = diff

# support out-of-tree builds by symlinking the makefile
BASE := $(dir $(realpath ${MAKEFILE_LIST}))
vpath %.cpp ${BASE}
vpath %.hpp ${BASE}

SOURCES := $(subst ${BASE}/,,$(wildcard ${BASE}/src/*.cpp))
HEADERS := $(subst ${BASE}/,,$(wildcard ${BASE}/src/*.hpp))
OBJECTS := $(patsubst src/%.cpp,obj/%.o,${SOURCES})
FORMATS := $(patsubst src/%.cpp,obj/%.formatted.cpp,${SOURCES})
FORMAT_TESTS := $(patsubst src/%.cpp,obj/%.formatted.ok,${SOURCES})
BINS := main

bins: ${BINS}
objects: ${OBJECTS}

%: obj/%.o
	${CXX} ${LDFLAGS} $^ ${LDLIBS} -o $@
obj/%.o: src/%.cpp ${HEADERS} | obj/.
	${CXX} ${CPPFLAGS} ${CXXFLAGS} -c -o $@ $<
obj/.:
	mkdir obj
obj/%.formatted.cpp: src/%.cpp main
	./main $< $@ obj/$*.error
obj/%.formatted.ok: src/%.cpp obj/%.formatted.cpp
	${DIFF} -ru $^
	touch $@

override CXXFLAGS += -std=c++0x

main: ${OBJECTS}

clean:
	rm -rf obj ${BINS}
test: format
format: ${FORMAT_TESTS}
