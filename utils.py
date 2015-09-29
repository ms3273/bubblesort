from pymtl import *
#=============================================================
# constant definition
#=============================================================

LOAD    = 0
STORE   = 1
CGT     = 2
SUB     = 3
CEZ     = 4
ADD     = 5
MUL     = 6
COPY    = 7
DEC     = 8
SWAP    = 9

nWid    = 16
nReg    = 4
nLogReg = 2
nPE     = 4

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
    s.des  = BitField( 7 )
