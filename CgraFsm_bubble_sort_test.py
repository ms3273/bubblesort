#=========================================================================
# test for CgraFsm.py
#=========================================================================

import pytest

from pymtl        import *
from pclib.test   import TestSource, TestSink
from CgraFsm_bubble_sort  import CgraFsm
from utils        import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, CgraFsm_model, src_mem_in_msgs, sink_mem_out_msgs, src_delay, sink_delay ):

    # Instantiate models
    
    s.src_mem_in   = TestSource (nWid, src_mem_in_msgs,     src_delay  )
    s.sink_mem_out = TestSink   (nWid, sink_mem_out_msgs,   sink_delay )

    s.CgraFsm = CgraFsm_model

  def elaborate_logic( s ):

    # Connect

    s.connect( s.src_mem_in.out,   s.CgraFsm.in_mem  )
    s.connect( s.sink_mem_out.in_, s.CgraFsm.out_mem )

  def done( s ):
    return s.src_mem_in.done and s.sink_mem_out.done

  def line_trace( s ):
    return s.src_mem_in.line_trace() + " | " + s.CgraFsm.line_trace() + " | " + s.sink_mem_out.line_trace()


#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_sel_test( ModelType, src_delay, sink_delay, test_verilog ):

  # test operands

  src_mem_in_msgs   = [0x7, 0x2, 0x8, 0x4, 22, 4, 19, 25]
  sink_mem_out_msgs = [0x1, 0x4, 2, 1]

  # Instantiate and elaborate the model

  model_under_test = ModelType()
  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, src_mem_in_msgs, sink_mem_out_msgs, src_delay, sink_delay )
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
  run_sel_test( CgraFsm, src_delay, sink_delay, test_verilog )
