#=========================================================================
# hybrid FSM-CGRA
#=========================================================================

from pymtl           import *
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from utils           import *
from cgra_bubble_sort        import CgraRTL
from fsm_bubble_sort         import fsm
from pclib.rtl       import SingleElementBypassQueue, SingleElementNormalQueue, NormalQueue
from pclib.ifcs                    import MemMsg, MemReqMsg, MemRespMsg
class CgraFsm( Model):

  def __init__( s ):

    # interface

    s.in_mem        = InValRdyBundle (MemReqMsg(1,32,nWid))  # 3 type, 0 opaque, 32 addr, 1 len, 16 data 
    s.out_mem       = OutValRdyBundle(MemRespMsg(1,  nWid))  # 3 type, 0 opaque,  2 test, 1 len, 16 data
    s.in_done       = InPort(1)            # loading data is done    

    s.cgra = CgraRTL()
    s.fsm  = fsm()

    # queue for control word
    #s.ctr_q = SingleElementBypassQueue[nPE](inst_msg())
    # s.ctr_q = SingleElementNormalQueue[nPE](inst_msg())
    #s.ctr_q = NormalQueue[nPE](2, inst_msg())

    # queue for cgra-to-fsm response

    s.resp_q = SingleElementBypassQueue[nPE](1)
    #s.resp_q = SingleElementNormalQueue[nPE](1)

    for x in range(nPE):
      s.connect(s.cgra.out_fsm[x], s.resp_q[x].enq       )
      s.connect(s.resp_q[x].deq,   s.fsm.in_[x]          )
      #s.connect (s.cgra.out_fsm[x] , s.fsm.in_[x]          )

     # s.connect(s.fsm.out[x],      s.ctr_q[x].enq        )
      #s.connect(s.ctr_q[x].deq,    s.cgra.in_control[x]  )
      s.connect(s.fsm.out[x], s.cgra.in_control[x])

    # test source to memory connection

    s.connect( s.in_mem,  s.cgra.in_mem     )
    s.connect( s.in_done,  s.fsm.in_done    )

    # test sink to memory connection

    s.connect( s.out_mem,         s.cgra.out_mem       )

    # MEM SOURCE SEL
    
    s.connect(s.cgra.ocm_reqs_sel,  s.fsm.ocm_reqs_sel  )
    s.connect(s.cgra.ocm_resps_sel, s.fsm.ocm_resps_sel )



  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.cgra.line_trace() + " | " + s.fsm.line_trace() # + " | pe0_rdy {} | fsm0rdy {} " .format(s.cgra.in_control[0].rdy,s.fsm.out[0].rdy)  



