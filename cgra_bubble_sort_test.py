#=========================================================================
# test for cgra.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.test   import TestSource, TestSink
from cgra_gcd     import CgraRTL
from utils        import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, cgra_model, src_mem_in_msgs, src_ctr_0_in_msgs, src_ctr_1_in_msgs, sink_mem_out_msgs, sink_fsm_0_out_msgs, sink_fsm_1_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    s.src_mem_in   = TestSource (nWid,       src_mem_in_msgs,   src_delay)
    s.src_ctr_0_in = TestSource (inst_msg(), src_ctr_0_in_msgs, src_delay)
    s.src_ctr_1_in = TestSource (inst_msg(), src_ctr_1_in_msgs, src_delay)

    s.sink_mem_out   = TestSink (nWid,       sink_mem_out_msgs,   sink_delay)
    s.sink_fsm_0_out = TestSink (1,          sink_fsm_0_out_msgs, sink_delay)
    s.sink_fsm_1_out = TestSink (1,          sink_fsm_1_out_msgs, sink_delay)

    s.cgra = cgra_model

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src_mem_in.out,     s.cgra.in_mem          )
    s.connect( s.src_ctr_0_in.out,   s.cgra.in_control[0]   )
    s.connect( s.src_ctr_1_in.out,   s.cgra.in_control[1]   )

    s.connect( s.sink_mem_out.in_,   s.cgra.out_mem         )
    s.connect( s.sink_fsm_0_out.in_, s.cgra.out_fsm[0]      )
    s.connect( s.sink_fsm_1_out.in_, s.cgra.out_fsm[1]      )

  def done( s ):
    return s.src_mem_in.done and s.src_ctr_0_in.done and s.src_ctr_1_in.done and s.sink_mem_out.done and s.sink_fsm_0_out.done and s.sink_fsm_1_out.done

  def line_trace( s ):
    return s.src_mem_in.line_trace() + " () " + s.cgra.line_trace() + " () " + s.sink_mem_out.line_trace()


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

  src_mem_in_msgs   = [0x4, 0x2]
  src_ctr_0_in_msgs = [inst(LOAD, 0, 0, 16 + 0), inst(LOAD, 0, 0, 16 + 1), inst(CGT, 0, 1, 0), inst(SUB, 0, 1, 16 + 4 + 0 ), inst(CGT, 0, 1, 0), inst(SUB, 1, 0, 16 + 4 + 1), inst(STORE, 0, 0, 0)]
  src_ctr_1_in_msgs = [inst(CEZ,  5, 0, 0), inst(CEZ,  5, 0, 0)]

  sink_mem_out_msgs   = [0x2]
  sink_fsm_0_out_msgs = [0x1, 0x0]
  sink_fsm_1_out_msgs = [0x0, 0x1]

  # Instantiate and elaborate the model

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, src_mem_in_msgs, src_ctr_0_in_msgs, src_ctr_1_in_msgs, sink_mem_out_msgs, sink_fsm_0_out_msgs, sink_fsm_1_out_msgs, src_delay, sink_delay )
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
  run_sel_test( test_verilog, CgraRTL, src_delay, sink_delay )
