#=========================================================================
# hybrid FSM-CGRA
#=========================================================================

from pymtl                         import *
from pclib.ifcs                    import InValRdyBundle, OutValRdyBundle
from utils                         import *
from pe                            import PeRTL
from pclib.rtl                     import SingleElementBypassQueue
from pclib.test                    import TestMemory
from pclib.ifcs                    import MemMsg, MemReqMsg, MemRespMsg

class CgraRTL( Model):

  def __init__( s ):

    # interface
    
    s.in_control   = InValRdyBundle[nPE](inst_msg()) # control word
    s.in_mem       = InValRdyBundle (nWid) 

    s.out_mem      = OutValRdyBundle(nWid)
    s.out_fsm      = OutValRdyBundle[nPE](1)  # response to FSM

    #Memory

    s.ocm = TestMemory( MemMsg(8 , 32, nWid) )  # nports, stall_prob, latency, mem_nbytes


    #PEs

    s.pe = PeRTL[nPE]()

    s.queue = SingleElementBypassQueue[2*(nPE-1)](nWid)

    for i in range(nPE - 1):
      s.connect (s.pe[i].out_neighbor[0],   s.queue[2*i].enq         )
      s.connect (s.queue[2*i].deq,          s.pe[i+1].in_neighbor[1] )

      s.connect (s.pe[i+1].out_neighbor[1], s.queue[2*i+1].enq       )
      s.connect (s.queue[2*i+1].deq,        s.pe[i].in_neighbor[0]   )

    for x in range(nPE):
      s.connect(s.in_control[x],     s.pe[x].in_control  )
      s.connect(s.out_fsm[x],        s.pe[x].out_fsm     )

    
    
    #Memory Connections
    
    s.connect(s.ocm.reqs[0],  s.pe[0].ocmreqs  )
    s.connect(s.ocm.resps[0], s.pe[1].ocmresps )

    s.connect(s.in_mem,              s.pe[0].in_mem      )
    s.connect(s.out_mem,             s.pe[0].out_mem     )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    msg = s.pe[0].line_trace()
    #for i in range(nPE-1):
    for i in range(1):
      msg = msg + " () " + s.pe[i+1].line_trace()
    return msg



