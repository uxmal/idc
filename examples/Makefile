# Makefile


PYTHON = python
export PYTHONPATH = ..

ARCH=$(shell uname -m)

CC = gcc

CFLAGS = -O

ifneq ($(ARCH),i686)
 ifeq ($(ARCH),x86_64)
# force generation of 32bit in 64bit systems
CFLAGS += -m32
 else
$(error An Intel x86 or AMD x86-64 machine is required to compile the examples.)
 endif
endif

# assume no stdlib nor builtins
CFLAGS += -ffreestanding

# optimization
CFLAGS += -fomit-frame-pointer
CFLAGS += -fno-optimize-sibling-calls
CFLAGS += -fno-merge-constants
CFLAGS += -fno-inline
CFLAGS += -foptimize-register-move
CFLAGS += -fcprop-registers

# i386 code output
CFLAGS += -march=i386

# use register arguments instead of stack arguments
CFLAGS += -mregparm=3
CFLAGS += -fargument-noalias

# don'te generate jump tables
#CFLAGS += -fno-jump-tables

# specify some clobbered/saved registers
CFLAGS += -fcall-used-eax -fcall-used-ebx -fcall-used-ecx -fcall-used-edx
CFLAGS += -fcall-saved-edi -fcall-saved-esi

# verbose asm output
#CFLAGS += -fverbose-asm


AS = as
ASFLAGS = 

LD = ld
LDFLAGS = 


all: \
	$(patsubst %.c,%.s,$(wildcard *.c)) \
	$(patsubst %.s,%.aterm,$(wildcard *.s))


%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.s: %.c
	$(CC) $(CFLAGS) -S $<

%.o: %.s
	$(AS) $(ASFLAGS) -o $@ $<

%: %.o
	$(LD) $(LDFLAGS) -o $@ $<

.PRECIOUS: %s

%.aterm: %.s
	$(PYTHON) ../translate.py $<


clean:
	rm -f $(patsubst %.s,%.aterm,$(wildcard *.s))
	rm -f $(patsubst %.c,%.s,$(wildcard *.c))


.PHONY: all clean
