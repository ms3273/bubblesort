#=========================================================================
# GCD FSM
#=========================================================================

from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.rtl   import *
from utils       import *

NUM_STATE       = 6
LOG_NUM_STATE   = 4

class fsm( Model ):

  #
  # Note: PE0 -- neighbor[0] --> PE1
  # Note: PE0 <-- neighbor[1] -- PE0

  # Constructor

  def __init__( s ):

    # Interface

    s.in_ = InValRdyBundle [nPE]( 1  )
    s.out = OutValRdyBundle[nPE]( inst_msg() )

    s.in_done = InPort(1)    # test memory transfer done

    s.ocm_reqs_sel  = OutPort(2)
    s.ocm_resps_sel = OutPort(4)

    # Register definition
    s.state = RegRst(LOG_NUM_STATE, 0)


    s.large   = RegRst(1,0)  # 1 bit data to be stored with 0 initialized, i.e PE0 has large value
    s.result  = RegRst(1,0)  # 1 bit data to be stored with 0 initialized, i.e PE0 has large value
    s.is_zero = RegRst(1,0)  # 1 bit data to be stored with 0 initialized, i.e PE0 has large value

    s.RD_ADDR = RegEnRst(32, 2)

    s.WR_ADDR = RegEnRst(32, 2) 

    s.test    = Wire(1)

    # State definition
    LOAD_TEST         = 0
    MEMREQ_DATASIZE   = 1
    MEMRESP_DATASIZE  = 2
    SIZE_COPY         = 3
    INIT_S0_READ      = 4
    INIT_S0_WRITE     = 5
    WRITE_COMP        = 6
    CMP_RESULT        = 7
    DEC_COUNTER       = 8
    CHECK_COUNTER     = 9
    OUTER_LOOP_DEC    = 10
    EXIT_CHECK        = 11
    EXIT_TRANSFER     = 12
    EXIT_DEC          = 13
    END_CHECK         = 14

    # Memory mux select
    TEST = Bits(2,0)
    PE0  = Bits(2,1)
    PE1  = Bits(2,2)

    # Memory base address
    BASE      = Bits(32,0)
#    RD_ADDR   = Bits(32,2)
#    WR_ADDR   = Bits(32,2)

    @s.combinational
    def combinational_module():

      s.ocm_reqs_sel.value  = PE1_MEM
      s.ocm_resps_sel.value = MEM_PROXY
      s.RD_ADDR.en.value    = 0
      s.WR_ADDR.en.value    = 0
      s.test.value          = 0
#      for x in range(nPE):
#        s.in_[x].rdy.value  = 0
#        s.out[x].val.value  = 0
#        s.out[x].msg.value  = 0

      #------------------------------------------------------------------
      # LOAD_TEST state
      #------------------------------------------------------------------
      # load data from test to ocm

      if s.state.out == LOAD_TEST:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        s.state.in_.value     = LOAD_TEST
        s.RD_ADDR.in_.value   = BASE + 2
        s.WR_ADDR.in_.value   = BASE + 2

        if s.in_done:
          s.state.in_.value     = MEMREQ_DATASIZE
          s.RD_ADDR.en.value    = 1
          s.WR_ADDR.en.value    = 1
  
        elif not s.in_done:
          s.ocm_reqs_sel.value = TEST_MEM
         
      #------------------------------------------------------------------
      # MEMREQ_DATASIZE state
      #------------------------------------------------------------------
      # load data size from 0x0 address of memory to reg4 of PE0

      if s.state.out == MEMREQ_DATASIZE:
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = MEMREQ_DATASIZE
        

        # connect proper muxes to/from memory
        s.test.value          = 1
        s.ocm_reqs_sel.value  = PE0_MEM
        # select the operation in PE[x]
        s.out[0].msg.ctl.value = MEM_REQ

        # set control signals in PE[x]
       

        # set mem_control in PE
        s.out[0].msg.rd_wr.value = TYPE_READ 
        s.out[0].msg.addr.value  = BASE
   
        # set valid signals
        s.out[0].val.value       = 1

        # condition for exiting this state        
        if 1:
          #print s.state.out
          s.state.in_.value   = MEMRESP_DATASIZE        

      #------------------------------------------------------------------
      # MEMRESP_DATASIZE state
      #------------------------------------------------------------------
      # load data size from 0x0 address of memory to reg4 of PE0

      if s.state.out == MEMRESP_DATASIZE:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = MEMRESP_DATASIZE
        
        # connect proper muxes to/from memory
        s.ocm_resps_sel.value  = MEM_PE1

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = DEC
        s.out[1].msg.ctl.value = MEM_RESP

        # set control signals in PE[x] 
        s.out[0].msg.src0.value = 4
        s.out[0].msg.des.value = 16+3

        s.out[1].msg.des.value = 16+8+3

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value       = 1
        s.out[1].val.value       = 1

        # condition for exiting this state
      #  if s.out[0].rdy:
        s.state.in_.value   = SIZE_COPY



      #------------------------------------------------------------------
      # SIZE_COPY state
      #------------------------------------------------------------------
      # load data size from 0x0 address of memory to reg4 of PE0

      if s.state.out == SIZE_COPY:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = SIZE_COPY
        
        # connect proper muxes to/from memory

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = COPY

        # set control signals in PE[x]
        s.out[0].msg.src0.value = 3 
        s.out[0].msg.des.value  = 16 + 2
        
        #s.out[1].msg.src0.value = 5
        #s.out[1].msg.des.value  = 16 + 3

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value       = 1
        #s.out[1].val.value       = 1

        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy :
        s.state.in_.value   = INIT_S0_READ


      #------------------------------------------------------------------
      # INIT_S0_READ state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == INIT_S0_READ:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0
        
        # set the next state register value in case we need to hold this state
        s.state.in_.value = INIT_S0_READ

        # connect proper muxes to/from memory
        s.ocm_reqs_sel.value  = PE0_MEM
        
        # select the operation in PE[x]
        s.out[0].msg.ctl.value = MEM_REQ

        # set control signals in PE[x]
        

        # set mem_control in PE
        s.out[0].msg.rd_wr.value = TYPE_READ 
        s.out[0].msg.addr.value  = s.RD_ADDR.out
        s.RD_ADDR.in_.value      = s.RD_ADDR.out + 2
 
        # set valid signals
        s.out[0].val.value       = 1

        # condition for exiting this state        
        #if s.out[0].rdy:
        s.state.in_.value   = INIT_S0_WRITE
        s.RD_ADDR.en.value  = 1

      #------------------------------------------------------------------
      # INIT_S0_WRITE and S1_READ state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == INIT_S0_WRITE:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = INIT_S0_WRITE
        
        # connect proper muxes to/from memory
        s.ocm_reqs_sel.value   = PE1_MEM

        s.ocm_resps_sel.value  = MEM_PE0

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = MEM_RESP
        s.out[1].msg.ctl.value = MEM_REQ

        # set control signals in PE[x] 
        s.out[0].msg.des.value = 16+0

        # set mem_control_signals
        s.out[1].msg.rd_wr.value = TYPE_READ 
        s.out[1].msg.addr.value  = s.RD_ADDR.out
        s.RD_ADDR.in_.value = s.RD_ADDR.out + 2


        # set valid signals
        s.out[0].val.value       = 1
        s.out[1].val.value       = 1
 
        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy:
        s.state.in_.value   = WRITE_COMP
        s.RD_ADDR.en.value  = 1


      #------------------------------------------------------------------
      # WRITE_COMP state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == WRITE_COMP:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = WRITE_COMP
        
        # connect proper muxes to/from memory
        if   s.large.out == 0: s.ocm_resps_sel.value  = MEM_PE1
        elif s.large.out == 1: s.ocm_resps_sel.value  = MEM_PE0
        # select the operation in PE[x]
        if s.large.out == 0:
          s.out[0].msg.ctl.value = CGT
          s.out[1].msg.ctl.value = MEM_RESP
        else:
          s.out[0].msg.ctl.value = MEM_RESP
          s.out[1].msg.ctl.value = CGT         

        # set control signals in PE[x]
        if s.large.out == 0: 
          s.out[0].msg.src0.value = 0          # source 0 PE[0]
          s.out[0].msg.src1.value = 4          # source 1 PE[1] (from neigbor 0)

          s.out[1].msg.des.value  = 16 + 8 + 0 # store in self PE[1] and pass a copy to neighbor 1

        else:
          s.out[0].msg.des.value  = 16 + 4 + 0 # store in self PE[0] and pass a copy to neighbor 0
 
          s.out[1].msg.src0.value = 5          # source 0 PE[0] (from neigbor 1)
          s.out[1].msg.src1.value = 0          # source 1 PE[1]

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value       = 1
        s.out[1].val.value       = 1
      
        if s.large.out == 0 and s.in_[0].val:
          s.in_[0].rdy.value = 1
          s.result.in_.value = s.in_[0].msg

        elif s.large.out == 1 and s.in_[1].val:
          s.in_[1].rdy.value = 1
          s.result.in_.value = s.in_[1].msg

        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy:
        s.state.in_.value   = CMP_RESULT



###################################################################################

      #------------------------------------------------------------------
      # CMP_RESULT state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == CMP_RESULT:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = CMP_RESULT

        # Large stored in PE[0]
        # check comparison and wr smaller data back to mem

        #if s.large.out == 0:

          # connect proper muxes to/from memory
        if   s.result.out == 1:              # src0 (PE0) is greater, store from PE1 
          s.ocm_reqs_sel.value  = PE1_MEM
 
        else:             # src1 (PE1) is greater, store from PE0
          s.ocm_reqs_sel.value  = PE0_MEM

        # select the operation in PE[x]
        if s.result.out == 1:
          s.out[1].msg.ctl.value = MEM_REQ
        else:
          s.out[0].msg.ctl.value = MEM_REQ

        # set control signals in PE[x]

        # set mem_control_signals
        if s.result.out == 1:
          s.out[1].msg.rd_wr.value = TYPE_WRITE
          s.out[1].msg.src0.value  = 0
          s.out[1].msg.addr.value  = s.WR_ADDR.out 
 
        else:
          s.out[0].msg.rd_wr.value = TYPE_WRITE
          s.out[0].msg.src0.value  = 0
          s.out[0].msg.addr.value  = s.WR_ADDR.out
        
        s.WR_ADDR.in_.value   = s.WR_ADDR.out + 2          

        # set valid signals and update the data stored in large register
        if   s.result.out == 1: 
          s.out[1].val.value   = 1
          s.large.in_.value    = 0

        else:
          s.out[0].val.value  = 1
          s.large.in_.value   = 1

        #if (s.in_[0].msg == 1 and s.out[1].rdy) or (s.in_[0].msg == 0 and s.out[0].rdy) :
        s.state.in_.value     = DEC_COUNTER
        s.WR_ADDR.en.value    = 1  # update write address
             
        #if (s.large.out == 0 ):
        #  s.in_[0].rdy.value = (s.in_[0].msg == 1 and s.out[1].rdy) or (s.in_[0].msg == 0 and s.out[0].rdy) 


      #------------------------------------------------------------------
      # DEC_COUNTER state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == DEC_COUNTER:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = DEC_COUNTER
        
        # connect proper muxes to/from memory

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = DEC
        s.out[1].msg.ctl.value = CEZ

        # set control signals in PE[x]
        s.out[0].msg.src0.value = 2          # source 2 PE[0]
        s.out[0].msg.des.value = 16 + 4 + 2      # source 1 PE[1] (from neigbor 0)

        s.out[1].msg.src0.value  = 5         # get value from PE[0] for CEZ 

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value       = 1
        s.out[1].val.value       = 1#s.out[0].rdy
     
        if s.in_[1].val:
          s.is_zero.in_.value =  s.in_[1].msg
          s.in_[1].rdy.value  =  1
 
        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy:
        s.state.in_.value   = CHECK_COUNTER



      #------------------------------------------------------------------
      # CHECK_COUNTER state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == CHECK_COUNTER:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = CHECK_COUNTER
        
        if s.is_zero.out == 0:    # s.in_[1].msg == 0 and s.in_[1].val:

          if s.large.out == 0:
            # connect proper muxes to/from memory
            s.ocm_reqs_sel.value   = PE1_MEM

            # select the operation in PE[x]
            s.out[1].msg.ctl.value = MEM_REQ

            # set control signals in PE[x]

            # set mem_control_signals
            s.out[1].msg.rd_wr.value = TYPE_READ 
            s.out[1].msg.addr.value  = s.RD_ADDR.out
            s.RD_ADDR.in_.value  = s.RD_ADDR.out + 2

            # set valid signals
            s.out[1].val.value    = 1#s.in_[1].val
            #s.in_[1].rdy.value    = 1#s.out[1].rdy

            # condition for exiting this state
            #if s.out[1].rdy and s.in_[1].val:
            s.state.in_.value    = WRITE_COMP
            s.RD_ADDR.en.value   = 1

          elif s.large.out == 1:
            # connect proper muxes to/from memory
            s.ocm_reqs_sel.value   = PE0_MEM

            # select the operation in PE[x]
            s.out[0].msg.ctl.value = MEM_REQ

            # set control signals in PE[x]

            # set mem_control_signals
            s.out[0].msg.rd_wr.value = TYPE_READ 
            s.out[0].msg.addr.value  = s.RD_ADDR.out
            s.RD_ADDR.in_.value      = s.RD_ADDR.out + 2
            

            # set valid signals
            s.out[0].val.value    = 1#s.in_[1].val
            #s.in_[1].rdy.value    = 1#s.out[0].rdy

            # condition for exiting this state
            #if s.out[0].rdy and s.in_[1].val:
            s.state.in_.value   = WRITE_COMP
            s.RD_ADDR.en.value  = 1

        else:

          if s.large.out == 0:
            # connect proper muxes to/from memory
            s.ocm_reqs_sel.value   = PE0_MEM

            # select the operation in PE[x]
            s.out[0].msg.ctl.value = MEM_REQ

            # set control signals in PE[x]
            s.out[0].msg.src0.value  = 0

            # set mem_control_signals
            s.out[0].msg.rd_wr.value = TYPE_WRITE 
            s.out[0].msg.addr.value  = s.WR_ADDR.out
            s.WR_ADDR.in_.value      = BASE + 2 
            s.RD_ADDR.in_.value      = BASE + 2
            s.large.in_.value        = 0

            # set valid signals
            s.out[0].val.value    = 1#s.in_[1].val
            #s.in_[1].rdy.value    = 1#s.out[0].rdy
      
            # condition for exiting this state
            #if s.out[0].rdy and s.in_[1].val:
            s.state.in_.value      = OUTER_LOOP_DEC
            s.WR_ADDR.en.value     = 1
            s.RD_ADDR.en.value  = 1

          elif s.large.out == 1:

            # connect proper muxes to/from memory
            s.ocm_reqs_sel.value   = PE1_MEM

            # select the operation in PE[x]
            s.out[1].msg.ctl.value = MEM_REQ

            # set control signals in PE[x]
            s.out[1].msg.src0.value  = 0

            # set mem_control_signals
            s.out[1].msg.rd_wr.value = TYPE_WRITE
            s.out[1].msg.addr.value  = s.WR_ADDR.out
            s.WR_ADDR.in_.value      = BASE + 2
            s.RD_ADDR.in_.value      = BASE + 2
            s.large.in_.value        = 0

            # set valid signals
            s.out[1].val.value       = 1#s.in_[1].val
            #s.in_[1].rdy.value       = 1#s.out[1].rdy
      
            # condition for exiting this state
            #if s.out[1].rdy and s.in_[1].val:
            s.state.in_.value      = OUTER_LOOP_DEC
            s.WR_ADDR.en.value     = 1 
            s.RD_ADDR.en.value  = 1



      #------------------------------------------------------------------
      # OUTER_LOOP_DEC state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == OUTER_LOOP_DEC:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = OUTER_LOOP_DEC

        # connect proper muxes to/from memory

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = DEC
        s.out[1].msg.ctl.value = CEZ

        # set control signals in PE[x]
        s.out[0].msg.src0.value = 3
        s.out[0].msg.des.value  = 16 + 4 + 3

        s.out[1].msg.src0.value = 5

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value   = 1#s.out[1].rdy
        s.out[1].val.value   = 1#s.out[0].rdy

        if s.in_[1].val:
          s.is_zero.in_.value =  s.in_[1].msg
          s.in_[1].rdy.value  =  1
    
        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy:
        s.state.in_.value   = EXIT_CHECK


      #------------------------------------------------------------------
      # EXIT_CHECK state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == EXIT_CHECK:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = EXIT_CHECK
        #s.in_[1].rdy.value = 1
        
        if s.is_zero.out == 0: #s.in_[1].msg == 0 and s.in_[1].val:

          # connect proper muxes to/from memory

          # select the operation in PE[x]
          s.out[0].msg.ctl.value = COPY
          # set control signals in PE[x]
          s.out[0].msg.src0.value = 3
          s.out[0].msg.des.value  = 16 + 2
          # set mem_control_signals

          # set valid signals
          s.out[0].val.value = 1 
          # condition for exiting this state
          s.state.in_.value   = INIT_S0_READ


        else:   #elif s.in_[1].msg == 1 and s.in_[1].val:

          # connect proper muxes to/from memory

          # select the operation in PE[x]

          # set control signals in PE[x]
          s.RD_ADDR.in_.value = BASE + 2
          s.RD_ADDR.en.value  = 1
          # set mem_control_signals

          # set valid signals
      
          # condition for exiting this state
          s.state.in_.value   = EXIT_TRANSFER

      #------------------------------------------------------------------
      # EXIT_TRANSFER state
      #------------------------------------------------------------------
      # load data size from 0x0 address of memory to reg4 of PE0

      if s.state.out == EXIT_TRANSFER:

        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = EXIT_TRANSFER
        
        # connect proper muxes to/from memory
        s.ocm_reqs_sel.value   = PE1_MEM


        # select the operation in PE[x]
        s.out[1].msg.ctl.value = MEM_REQ

        # set control signals in PE[x] 
      
        # set mem_control_signals
        s.out[1].msg.rd_wr.value = TYPE_READ
        s.out[1].msg.addr.value  = s.RD_ADDR.out
        s.RD_ADDR.in_.value      = s.RD_ADDR.out + 2        

        # set valid signals
        s.out[1].val.value       = 1
      
        # condition for exiting this state
        #if s.out[1].rdy:
        s.state.in_.value   = EXIT_DEC
        s.RD_ADDR.en.value  = 1

      #------------------------------------------------------------------
      # EXIT_DEC state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == EXIT_DEC:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = EXIT_DEC

        # connect proper muxes to/from memory
        s.ocm_resps_sel.value  = MEM_TEST

        # select the operation in PE[x]
        s.out[0].msg.ctl.value = CEZ
        s.out[1].msg.ctl.value = DEC

        # set control signals in PE[x]
        s.out[0].msg.src0.value = 4

        s.out[1].msg.src0.value = 3
        s.out[1].msg.des.value  = 16 + 8 + 3

        # set mem_control_signals

        # set valid signals
        s.out[0].val.value   = 1#s.out[1].rdy
        s.out[1].val.value   = 1#s.out[0].rdy      

        if s.in_[0].val:
          s.is_zero.in_.value =  s.in_[0].msg
          s.in_[0].rdy.value  =  1
    
        # condition for exiting this state
        #if s.out[0].rdy and s.out[1].rdy:
        s.state.in_.value   = END_CHECK



      #------------------------------------------------------------------
      # END_CHECK state
      #------------------------------------------------------------------
      # read the first operand from memory

      if s.state.out == END_CHECK:
        
        for x in range(nPE):
          s.in_[x].rdy.value  = 0
          s.out[x].val.value  = 0
          s.out[x].msg.value  = 0

        # set the next state register value in case we need to hold this state
        s.state.in_.value     = END_CHECK
       # s.in_[0].rdy.value = 1
        
        if s.is_zero.out == 0: #s.in_[0].msg == 0 and s.in_[0].val:

          # connect proper muxes to/from memory

          # select the operation in PE[x]

          # set control signals in PE[x]

          # set mem_control_signals

          # set valid signals
    
          # condition for exiting this state
          s.state.in_.value   = EXIT_TRANSFER

        else:   #elif s.in_[0].msg == 1 and s.in_[0].val:
          s.state.in_.value   = LOAD_TEST


  

  def line_trace ( s ):
    
    state2char = {
      0   : "LOAD_TEST       ",
      1   : "MEMREQ_DATASIZE ",
      2   : "MEMRESP_DATASIZE",
      3   : "SIZE_COPY       ",
      4   : "INIT_S0_READ    ",
      5   : "INIT_S0_WRITE   ",
      6   : "WRITE_COMP      ",
      7   : "CMP_RESULT      ",
      8   : "DEC_COUNTER     ",
      9   : "CHECK_COUNTER   ",
      10  : "OUTER_LOOP_DEC  ",
      11  : "EXIT_CHECK      ",
      12  : "EXIT_TRANSFER   ",
      13  : "EXIT_DEC        ",
      14  : "END_CHECK       ",
    }

    s.state_str = state2char[s.state.out.uint()]

    return "{}".format( s.state_str )
