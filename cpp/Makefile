# http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/
CPPFLAGS += -std=c++14 -g -Iinc -Wall
CXX = g++-5
SRCS = $(shell find . -name "*.cpp")


DEPDIR := .d
$(shell mkdir -p $(DEPDIR) >/dev/null)
BINDIR := bin
$(shell mkdir -p $(BINDIR) >/dev/null)
DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.Td

COMPILE = $(CXX) $(DEPFLAGS) $(CXXFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -c
POSTCOMPILE = mv -f $(DEPDIR)/$*.Td $(DEPDIR)/$*.d

vscode: clean all

all: csfer

csfer: $(SRCS:%.cpp=%.o)
	$(CXX) $(DEPFLAGS) $(CXXFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -o $(BINDIR)/$@ $^
	@echo csfer made.


%.o : %.cxx
%.o : %.cxx $(DEPDIR)/%.d
	$(COMPILE) $(OUTPUT_OPTION) $<
	$(POSTCOMPILE)

$(DEPDIR)/%.d: ;
.PRECIOUS: $(DEPDIR)/%.d

-include $(patsubst %,$(DEPDIR)/%.d,$(basename $(SRCS)))

clean:
	@echo $(SRCS)
	rm -f csfer
	find . -name '*.o' -delete