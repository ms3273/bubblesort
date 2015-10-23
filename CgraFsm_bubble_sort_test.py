#=========================================================================
# test for CgraFsm.py
#=========================================================================

import pytest

from pymtl                import *
from pclib.test           import TestSource, TestSink
from CgraFsm_bubble_sort  import CgraFsm
from utils                import *
from pclib.ifcs                    import MemMsg, MemReqMsg, MemRespMsg
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, CgraFsm_model, src_mem_in_msgs, sink_mem_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    s.src_mem_in     = TestSource (MemReqMsg(1,32,nWid), src_mem_in_msgs,     src_delay  )
    s.sink_mem_out   = TestSink   (MemRespMsg(1,  nWid), sink_mem_out_msgs,   sink_delay )

    s.CgraFsm = CgraFsm_model

  def elaborate_logic( s ):

    # Connect

    # test to DUT

    s.connect( s.src_mem_in.out,   s.CgraFsm.in_mem  )
    s.connect( s.src_mem_in.done,  s.CgraFsm.in_done )

    # DUT to test
    s.connect( s.sink_mem_out.in_,   s.CgraFsm.out_mem       )

  def done( s ):
    return s.src_mem_in.done and s.sink_mem_out.done

  def line_trace( s ):
    return s.src_mem_in.line_trace() + " | " + s.CgraFsm.line_trace() + " | " + s.sink_mem_out.line_trace()

#             0b    32b         1b     16b
#          opaque  addr               data
#    3b    nbits   nbits       calc   nbits
#  +------+------+-----------+------+-----------+
#  | type |opaque| addr      | len  | data      |
#  +------+------+-----------+------+-----------+

#             0b            1b    16b   
#          opaque                data
#    3b    nbits   2b     calc   nbits
#  +------+------+------+------+-----------+
#  | type |opaque| test | len  | data      |
#  +------+------+------+------+-----------+



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

def run_sel_test( ModelType, src_delay, sink_delay, test_verilog ):

  # test operands



  src_mem_in_msgs   = [memreq(1, 0x0, 0, 6), memreq(1, 0x2, 0, 5), memreq(1, 0x4, 0, 3), memreq(1, 0x6, 0, 4), memreq(1, 0x8, 0, 19), memreq(1, 0xa, 0, 1), memreq(1, 0xc, 0, 7) ]



  sink_mem_out_msgs = [memresp(0, 0, 0, 1), memresp(0, 0, 0, 3), memresp(0,0,0, 4), memresp(0,0,0, 5), memresp(0, 0, 0, 7), memresp(0, 0, 0, 19)]


  # Instantiate and elaborate the model

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, src_mem_in_msgs, sink_mem_out_msgs, src_delay, sink_delay )
  model.vcd_file = "regincr-sim.vcd"
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation
  a = 0

  print()

  sim.reset()
  while not model.done():
    a = a + 1
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  ( 0,  0),
])
def test( src_delay, sink_delay, test_verilog ):
  run_sel_test( CgraFsm, src_delay, sink_delay, test_verilog )
