#=========================================================================
# GCD FSM
#=========================================================================

from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.rtl   import RegRst
from utils       import *

NUM_STATE       = 5
LOG_NUM_STATE   = 3

class fsm( Model ):

  # Constructor

  def __init__( s ):

    # Interface

    s.in_ = InValRdyBundle [nPE]( 1  )
    s.out = OutValRdyBundle[nPE]( inst_msg() )

    # Register definition
    s.state = RegRst(LOG_NUM_STATE, 0)

    # State definition
    INIT_S0  = 0
    INIT_S1  = 1
    CALC_S0  = 2
    CALC_S1  = 3
    DONE     = 4

    @s.combinational
    def combinational_module():

      #------------------------------------------------------------------
      # INIT_S0 state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == INIT_S0:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value = INIT_S0

        # LOAD to register 0
        s.out[0].msg.ctl.value = LOAD
        s.out[0].msg.des.value = 16 + 0

        if s.out[0].rdy: 
          s.out[0].val.value = 1
          s.state.in_.value  = INIT_S1


      #------------------------------------------------------------------
      # INIT_S1 state
      #------------------------------------------------------------------
      # read the second operand from memory

      if s.state.out == INIT_S1:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value = INIT_S1

        # LOAD to register 1
        s.out[0].msg.ctl.value = LOAD
        s.out[0].msg.des.value = 16 + 1

        if s.out[0].rdy: 
          s.out[0].val.value = 1
          s.state.in_.value  = CALC_S0


      #------------------------------------------------------------------
      # CALC_S0 state
      #------------------------------------------------------------------
      # send out CGT instruction

      if s.state.out == CALC_S0:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value = CALC_S0

        s.in_[1].rdy.value = 1
        # termination condition
        if s.in_[1].val and (s.in_[1].msg == 1): 
          s.state.in_.value = DONE

        else:
          # CGT r0 > r1 ?
          s.out[0].msg.ctl.value  = CGT
          s.out[0].msg.src0.value = 0
          s.out[0].msg.src1.value = 1

          if s.out[0].rdy: 
            s.out[0].val.value = 1
            s.state.in_.value  = CALC_S1


      #------------------------------------------------------------------
      # CALC_S1 state
      #------------------------------------------------------------------
      # send out SUB instruction

      if s.state.out == CALC_S1:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value  = CALC_S1
        s.in_[1].rdy.value = 1
        # termination condition
        if s.in_[1].val and (s.in_[1].msg == 1): 
          s.state.in_.value = DONE

        else:
          # send out SUB instruction based on the result from CGT
          if s.in_[0].val:
            if s.in_[0].msg == 1:  # r0 > r1: do r0-r1 --> r0
              s.out[0].msg.ctl.value  = SUB
              s.out[0].msg.src0.value = 0
              s.out[0].msg.src1.value = 1
              s.out[0].msg.des.value  = 16 + 4 + 0

            elif s.in_[0].msg == 0: # r0 < r1: do r1-r0 --> r1
              s.out[0].msg.ctl.value  = SUB
              s.out[0].msg.src0.value = 1
              s.out[0].msg.src1.value = 0
              s.out[0].msg.des.value  = 16 + 4 + 1

            # also send out CEZ instruction
            s.out[1].msg.ctl.value  = CEZ
            s.out[1].msg.src0.value = 5

            if s.out[0].rdy and s.out[1].rdy: 
              # only goes to the next state when both SUB and CEZ are successfully issued
              s.in_[0].rdy.value = 1

              s.out[0].val.value = 1
              s.out[1].val.value = 1
              s.state.in_.value  = CALC_S0


      #------------------------------------------------------------------
      # DONE state
      #------------------------------------------------------------------
      # send out STORE instruction

      if s.state.out == DONE:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value = DONE

        # STORE value of register 0 to memory
        s.out[0].msg.ctl.value  = STORE
        s.out[0].msg.src0.value = 1

        if s.out[0].rdy: 
          s.state.in_.value  = INIT_S0
          s.out[0].val.value = 1


  def line_trace ( s ):
    
    state2char = {
      0  : "INIT_S0",
      1  : "INIT_S1",
      2  : "CALC_S0",
      3  : "CALC_S1",
      4  : "DONE   ",
    }

    s.state_str = state2char[s.state.out.uint()]

    return "({})".format( s.state_str )
