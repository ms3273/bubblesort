#=========================================================================
# test for fsm.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.test   import TestSource, TestSink
from fsm_gcd      import fsm
from utils        import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, fsm_model, src_0_in_msgs, src_1_in_msgs, sink_0_out_msgs, sink_1_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    s.src_0_in = TestSource (1, src_0_in_msgs, src_delay)
    s.src_1_in = TestSource (1, src_1_in_msgs, src_delay)

    s.sink_0_out = TestSink (inst_msg(), sink_0_out_msgs, sink_delay)
    s.sink_1_out = TestSink (inst_msg(), sink_1_out_msgs, sink_delay)

    s.fsm = fsm_model

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src_0_in.out,   s.fsm.in_[0] )
    s.connect( s.src_1_in.out,   s.fsm.in_[1] )

    s.connect( s.sink_0_out.in_, s.fsm.out[0] )
    s.connect( s.sink_1_out.in_, s.fsm.out[1] )

  def done( s ):
    return s.src_0_in.done and s.src_1_in.done and s.sink_0_out.done and s.sink_1_out.done

  def line_trace( s ):
    return s.src_0_in.line_trace() + "()" + s.src_1_in.line_trace() + "()" + s.sink_0_out.line_trace() + "()" + s.sink_1_out.line_trace() + "()" + s.fsm.line_trace()


def inst(opcode, src0, src1, des):
  msg = inst_msg()
  msg.ctl  = opcode
  msg.src0 = src0
  msg.src1 = src1
  msg.des  = des
  return msg


#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_sel_test( test_verilog, ModelType, src_delay, sink_delay ):

  # test operands

  src_0_in_msgs = [0x1, 0x0]
  src_1_in_msgs = [0x0, 0x0, 0x0, 0x0, 0x0, 0x1]

  sink_0_out_msgs = [inst(LOAD,0,0,16 + 0), inst(LOAD,0,0,16 + 1), inst(CGT,0,1,0), inst(SUB,0,1,16 + 4 + 0), inst(CGT,0,1,0), inst(SUB,1,0,16 + 4 + 1), inst(CGT,0,1,0), inst(STORE,0,0,0)]
  sink_1_out_msgs = [inst(CEZ, 5,0,0), inst(CEZ, 5,0,0)]

  # Instantiate and elaborate the model

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, src_0_in_msgs, src_1_in_msgs, sink_0_out_msgs, sink_1_out_msgs, src_delay, sink_delay )
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
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay, sink_delay', [
  ( 0,  0),
])
def test( src_delay, sink_delay, test_verilog ):
  run_sel_test( test_verilog, fsm, src_delay, sink_delay )
