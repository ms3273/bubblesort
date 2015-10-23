from pymtl import *
#=============================================================
# constant definition
#=============================================================

MEM_REQ  = 9
MEM_RESP = 1
CGT      = 2
SUB      = 3
CEZ      = 4
ADD      = 5
MUL      = 6
COPY     = 7
DEC      = 8

nWid    = 16
nReg    = 4
nLogReg = 2
nPE     = 4

TEST_MEM  = 0
PE0_MEM   = 1
PE1_MEM   = 2

MEM_TEST = 1
MEM_PE0  = 2
MEM_PE1  = 4
MEM_PROXY= 8

TYPE_READ  = 0
TYPE_WRITE = 1
#=============================================================
# instruction msg
#=============================================================
class inst_msg( BitStructDefinition ):

  def __init__( s ):

    s.ctl  = BitField( 4 )
    s.src0 = BitField( 3 )
    s.src1 = BitField( 3 )

    # for destination, bits 0~1 encodes one of the four local
    # registers, then the other two bits are used as one-hot
    # encoding for neighbors. i.e., if bit 2 is set, then send
    # result to right neighbor, if bit 3 is set, then send
    # result to left neighbor. If both bit 2 and bit 3 are set,
    # then send result to both neighbors.
    s.des   = BitField( 5 )

    #memory control signals
    s.rd_wr = BitField( 1 )
    s.addr  = BitField( 32 )

#class inst_mem( BitStructDefinition ):
#
#  def __init__( s ):
#
#    s.rd_wr = BitField( 1 )
#    s.rd_wr = BitField( 1 )
#
