#=========================================================================
# hybrid FSM-CGRA
#=========================================================================

from pymtl                         import *
from pclib.ifcs                    import InValRdyBundle, OutValRdyBundle
from utils                         import *
from pe                            import PeRTL
from pclib.rtl                     import *
from pclib.rtl.onehot              import Demux
from pclib.test                    import TestMemory
from pclib.ifcs                    import MemMsg, MemReqMsg, MemRespMsg



class CgraRTL( Model):

  def __init__( s ):

    # interface
    
    s.in_control   = InValRdyBundle[nPE](inst_msg()) # control word

    s.out_fsm      = OutValRdyBundle[nPE](1)  # response to FSM

    s.in_mem       = InValRdyBundle (MemReqMsg(1,32,nWid)) 
    s.out_mem      = OutValRdyBundle(MemRespMsg(1,  nWid))
#    s.out_mem_proxy = OutValRdyBundle(MemRespMsg(1, nWid))

    s.ocm_reqs_sel  = InPort(2)
    s.ocm_resps_sel = InPort(4)

    #Memory

    s.ocm = TestMemory( MemMsg(1 , 32, nWid) )  # nports, stall_prob, latency, mem_nbytes
    s.wr_capture = RegRst (MemRespMsg(1,nWid), 0)


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

    
    # mux to select the connection to occm
    s.mem_reqs_sel  = m = Mux(dtype = MemReqMsg(1,32,nWid), nports = 3)
    s.connect_pairs(
      m.in_[0],  s.in_mem.msg,
      m.in_[1],  s.pe[0].ocmreqs.msg,
      m.in_[2],  s.pe[1].ocmreqs.msg,
      m.sel,     s.ocm_reqs_sel,
      m.out,     s.ocm.reqs[0].msg,
    )

    # Demux to select connect from ocm
    s.mem_resps_sel = m = Demux (nports = 4, dtype = MemRespMsg(1,  nWid))
    s.connect_pairs(
      m.out[0],  s.out_mem.msg,
      m.out[1],  s.pe[0].ocmresps.msg,
      m.out[2],  s.pe[1].ocmresps.msg,
#      m.out[3],  s.out_mem_proxy.msg,
      m.out[3],  s.wr_capture.in_,
      m.in_,     s.ocm.resps[0].msg,
      m.sel,     s.ocm_resps_sel,
    )    
    

    s.test = Wire(1)
    @s.combinational
    def connections():
      s.test.value = 0
      s.in_mem.rdy.value         = 0
#      s.pe[0].ocmreqs.rdy.value  = 0
#      s.pe[1].ocmreqs.rdy.value  = 0

      s.ocm.reqs[0].val.value    = 0
      
      s.out_mem.val.value         = 0
#      s.pe[0].ocmresps.val.value  = 0
#      s.pe[1].ocmresps.val.value  = 0
#      s.out_mem_proxy.val.value   = 0
      s.ocm.resps[0].rdy.value    = 0

#      s.ocm_reqs_sel.value = 0
      if(s.ocm_reqs_sel == TEST_MEM):     
        s.in_mem.rdy.value         = s.ocm.reqs[0].rdy
        s.ocm.reqs[0].val.value    = s.in_mem.val
        s.pe[0].ocmreqs.rdy.value  = 0
        s.pe[1].ocmreqs.rdy.value  = 0

      elif(s.ocm_reqs_sel == PE0_MEM):
        s.pe[0].ocmreqs.rdy.value  = s.ocm.reqs[0].rdy
        s.ocm.reqs[0].val.value    = s.pe[0].ocmreqs.val
        s.pe[1].ocmreqs.rdy.value  = 0

      elif(s.ocm_reqs_sel == PE1_MEM):
        s.pe[1].ocmreqs.rdy.value  = s.ocm.reqs[0].rdy
        s.ocm.reqs[0].val.value    = s.pe[1].ocmreqs.val
        s.pe[0].ocmreqs.rdy.value  = 0


#      s.ocm_resps_sel.value = MEM_TEST
      if (s.ocm_resps_sel == MEM_TEST):
        s.out_mem.val.value        = s.ocm.resps[0].val
        s.ocm.resps[0].rdy.value   = s.out_mem.rdy
        s.pe[0].ocmresps.val.value  = 0
        s.pe[1].ocmresps.val.value  = 0


      elif (s.ocm_resps_sel == MEM_PE0):
        s.pe[0].ocmresps.val.value = s.ocm.resps[0].val
        s.ocm.resps[0].rdy.value   = s.pe[0].ocmresps.rdy
        s.pe[1].ocmresps.val.value  = 0

      elif (s.ocm_resps_sel == MEM_PE1):
        s.pe[1].ocmresps.val.value = s.ocm.resps[0].val
        s.ocm.resps[0].rdy.value   = s.pe[1].ocmresps.rdy
        s.pe[0].ocmresps.val.value  = 0

      elif (s.ocm_resps_sel == MEM_PROXY):
      #  s.out_mem_proxy.val.value = s.ocm.resps[0].val
        s.ocm.resps[0].rdy.value   =  1
        s.pe[0].ocmresps.val.value  = 0        
        s.pe[1].ocmresps.val.value  = 0

#      s.test.value = s.ocm_resps_sel == MEM_PROXY


  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
#    msg = s.pe[0].line_trace()
#    #for i in range(nPE-1):
#    for i in range(1):
#      msg = msg + " () " + s.pe[i+1].line_trace()
    return " req_rdy: {}| req_val: {}| resp_rdy: {} | resp_val: {}| pe0_val: {}| pe0_rdy: {}" .format(s.ocm.reqs[0].rdy, s.ocm.reqs[0].val, s.ocm.resps[0].rdy, s.ocm.resps[0].val, s.pe[0].ocmresps.val, s.pe[0].in_control.rdy ) + "() OCM - " + s.ocm.line_trace()



