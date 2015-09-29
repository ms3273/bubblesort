#=========================================================================
# hybrid FSM-CGRA
#=========================================================================

from pymtl           import *
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from utils           import *
from cgra_bubble_sort        import CgraRTL
from fsm_bubble_sort         import fsm
from pclib.rtl       import SingleElementBypassQueue, SingleElementNormalQueue, NormalQueue

class CgraFsm( Model):

  def __init__( s ):

    # interface

    s.in_mem       = InValRdyBundle (nWid) 
    s.out_mem      = OutValRdyBundle(nWid)

    s.cgra = CgraRTL()
    s.fsm  = fsm()

    # queue for control word
    #s.ctr_q = SingleElementBypassQueue[nPE](inst_msg())
    #s.ctr_q = SingleElementNormalQueue[nPE](inst_msg())
    s.ctr_q = NormalQueue[nPE](2, inst_msg())

    # queue for cgra-to-fsm response
    s.resp_q = SingleElementBypassQueue[nPE](1)
    #s.resp_q = SingleElementNormalQueue[nPE](1)

    for x in range(nPE):
      s.connect(s.cgra.out_fsm[x], s.resp_q[x].enq       )
      s.connect(s.resp_q[x].deq,   s.fsm.in_[x]          )

      s.connect(s.fsm.out[x],      s.ctr_q[x].enq        )
      s.connect(s.ctr_q[x].deq,    s.cgra.in_control[x]  )

    s.connect(s.in_mem,            s.cgra.in_mem         )
    s.connect(s.out_mem,           s.cgra.out_mem        )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.cgra.line_trace() + " | " + s.fsm.line_trace()



