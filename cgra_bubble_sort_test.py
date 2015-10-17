#=========================================================================
# test for cgra.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.test   import TestSource, TestSink
from cgra_bubble_sort    import CgraRTL
from utils        import *
from pclib.ifcs                    import MemMsg, MemReqMsg, MemRespMsg
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

#  def __init__( s, cgra_model, src_mem_in_msgs, src_ctr_0_in_msgs, src_ctr_1_in_msgs, sink_mem_out_msgs, sink_fsm_0_out_msgs, sink_fsm_1_out_msgs, src_delay, sink_delay ):

  def __init__( s, cgra_model, src_mem_in_msgs,sink_mem_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    s.src_mem_in   = TestSource (MemReqMsg(1,32,nWid),       src_mem_in_msgs,   1)
#    s.src_ctr_0_in = TestSource (inst_msg(), src_ctr_0_in_msgs, src_delay)
#    s.src_ctr_1_in = TestSource (inst_msg(), src_ctr_1_in_msgs, src_delay)
#
    s.sink_mem_out   = TestSink (MemRespMsg(1,nWid), sink_mem_out_msgs,   sink_delay)
#    s.sink_fsm_0_out = TestSink (1,          sink_fsm_0_out_msgs, sink_delay)
#    s.sink_fsm_1_out = TestSink (1,          sink_fsm_1_out_msgs, sink_delay)

#    s.reqs_sel   = TestSource ( 2,        reqs_sel_msg,   src_delay)
    s.cgra       = cgra_model

  def elaborate_logic( s ):

    # Connect

    s.connect (s.src_mem_in.out,  s.cgra.in_mem)
    s.connect (s.sink_mem_out.in_, s.cgra.out_mem)

  def done( s ):
    return  s.src_mem_in.done and s.sink_mem_out.done

  def line_trace( s ):
    return s.src_mem_in.line_trace() + "()" + s.sink_mem_out.line_trace() + "()" + s.cgra.line_trace() + "()DONE {}" .format(s.src_mem_in.done)


def inst(opcode, src0, src1, des, rd_wr, addr):
  msg = inst_msg()
  msg.ctl   = Bits( 4, opcode)
  msg.src0  = Bits( 3, src0  )
  msg.src1  = Bits( 3, src1  )
  msg.des   = Bits( 5, des   )
  msg.rd_wr = Bits( 1, rd_wr )
  msg.addr  = Bits(32, addr  )
  return msg

def memreq(typ, addr1, len, data):
  msg       = MemReqMsg(1,32,nWid)
  msg.type_ = Bits( 3,  typ   )
  msg.opaque= Bits( 1,  0     )
  msg.addr  = Bits( 32, addr1 )
  msg.len   = Bits( 1,  len   )
  msg.data  = Bits( 16, data  )
  return msg

def memresp(typ, test, len, data):
  msg = MemRespMsg(1,nWid)
  msg.type_ = Bits( 3,  typ   )
  msg.opaque= Bits( 1,  0    )
  msg.test  = Bits( 2, test  )
  msg.len   = Bits( 1,  len   )
  msg.data  = Bits( 16, data  )
  return msg


#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_sel_test( test_verilog, ModelType, src_delay, sink_delay ):

  # test operands

  src_mem_in_msgs    = [memreq(1, 0x0, 0, 14),memreq(1, 0x2, 0, 16), memreq(1, 0x4, 0, 18),  memreq(0, 0x2, 0,0)]

  sink_mem_out_msgs  = [memresp(1, 0, 0, 0),  memresp(1, 0, 0, 0),   memresp(1, 0, 0, 0),    memresp(0, 0, 0, 16)]


  # Instantiate and elaborate the model

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model =  TestHarness( model_under_test, src_mem_in_msgs,sink_mem_out_msgs, src_delay, sink_delay)
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()
  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  #sim.print_line_trace()



#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  ( 0,  0),
])
def test( src_delay, sink_delay, test_verilog ):
  run_sel_test( test_verilog, CgraRTL, src_delay, sink_delay )
