#=========================================================================
# PE model for hybrid FSM-CGRA
#=========================================================================

from pymtl           import *
from pclib.ifcs      import InValRdyBundle, OutValRdyBundle
from utils           import *
from pclib.rtl       import RegisterFile
from pclib.ifcs      import MemMsg, MemReqMsg, MemRespMsg

class PeRTL( Model):

  def __init__( s ):

    # interface
    
    s.in_control   = InValRdyBundle     (inst_msg() ) # control word
    s.in_mem       = InValRdyBundle     (nWid) 
    s.in_neighbor  = InValRdyBundle[2]  (nWid)

    s.out_mem      = OutValRdyBundle    (nWid)
    s.out_fsm      = OutValRdyBundle    (1)    # response to FSM
    s.out_neighbor = OutValRdyBundle[2] (nWid)

    s.ocmreqs      = OutValRdyBundle    (MemReqMsg(8,32,nWid))
    s.ocmresps     = InValRdyBundle     (MemRespMsg(8,  nWid))


    # PE local register file

    s.rf = RegisterFile( nWid, nReg, 2, 1 )

    # temporary variables

    s.src0_tmp = Wire( nWid )
    s.src1_tmp = Wire( nWid )
    s.des_tmp  = Wire( nWid )
    s.go       = Wire( 1 )

  def elaborate_logic( s ):

    @s.combinational
    def logic():

      # initializing outputs
      s.in_control.rdy.value      = 0
      s.in_mem.rdy.value          = 0
      s.in_neighbor[0].rdy.value  = 0
      s.in_neighbor[1].rdy.value  = 0
      s.out_mem.val.value         = 0
      s.out_mem.msg.value         = 0
      s.out_fsm.val.value         = 0      
      s.out_fsm.msg.value         = 0
      s.out_neighbor[0].val.value = 0
      s.out_neighbor[0].msg.value = 0
      s.out_neighbor[1].val.value = 0
      s.out_neighbor[1].msg.value = 0
      s.rf.wr_en.value            = 0
      if s.in_control.val:
        #=========================================================================
        # load
        #=========================================================================
        if s.in_control.msg.ctl == LOAD:

          s.go.value = 1

          if s.in_mem.val:
         
            s.des_tmp.value    = s.in_mem.msg 
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp

            if s.in_control.msg.des[nLogReg]:
              s.out_neighbor[0].msg.value = s.des_tmp
              if not s.out_neighbor[0].rdy: s.go.value = 0

            if s.in_control.msg.des[nLogReg+1]:
              s.out_neighbor[1].msg.value = s.des_tmp
              if not s.out_neighbor[1].rdy: s.go.value = 0

          else:
            s.go.value = 0

          if s.go:
            s.in_control.rdy.value = 1
            s.in_mem.rdy.value     = 1
            if s.in_control.msg.des[nLogReg]:
              s.out_neighbor[0].val.value = 1
            if s.in_control.msg.des[nLogReg + 1]:
              s.out_neighbor[1].val.value = 1
            if s.in_control.msg.des[nLogReg + 2]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # store
        #=========================================================================
        elif s.in_control.msg.ctl == STORE:
          if s.out_mem.rdy:
            s.in_control.rdy.value = 1
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.out_mem.val.value    = 1
            s.out_mem.msg.value    = s.rf.rd_data[0]


        #=========================================================================
        # compare-great-than
        #=========================================================================
        # We assume the result of CGT always goes to out_fsm. 
        # this is because CGT generates 1-bit control signal, which we assume will 
        # be handled by the FSM

        elif s.in_control.msg.ctl == CGT:
          if s.out_fsm.rdy:
        
            s.go.value = 1

            # src0
            if s.in_control.msg.src0 < nReg:
              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              if s.in_neighbor[s.in_control.msg.src0[0]].val:
                s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
              else: s.go.value = 0
      
              
            # src1
            if s.in_control.msg.src1 < nReg:
              s.rf.rd_addr[1].value  = s.in_control.msg.src1
              s.src1_tmp.value       = s.rf.rd_data[1]

            elif s.in_control.msg.src1 >= nReg:
              if s.in_neighbor[s.in_control.msg.src1[0]].val:
                s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1[0]].msg
              else: s.go.value = 0

            # compute
            if s.src0_tmp >= s.src1_tmp: s.out_fsm.msg.value = 1
            else: s.out_fsm.msg.value = 0
       
            # set control signals
            if s.go:
              s.in_control.rdy.value = 1
              s.out_fsm.val.value    = 1
              if s.in_control.msg.src0 >= nReg:
                s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1
              if s.in_control.msg.src1 >= nReg:
                s.in_neighbor[s.in_control.msg.src1[0]].rdy.value = 1


        #=========================================================================
        # compare-equal-zero
        #=========================================================================
        elif s.in_control.msg.ctl == CEZ:

          if s.out_fsm.rdy:
        
            s.go.value = 1

            # src0
            if s.in_control.msg.src0 < nReg:
              s.rf.rd_addr[0].value  = s.in_control.msg.src0
              s.src0_tmp.value       = s.rf.rd_data[0]

            elif s.in_control.msg.src0 >= nReg:
              if s.in_neighbor[s.in_control.msg.src0[0]].val:
                s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
              else: s.go.value = 0
      
            # compute
            if s.src0_tmp == 0: s.out_fsm.msg.value = 1
            else: s.out_fsm.msg.value = 0
            
            # set control signals
            if s.go:
              s.in_control.rdy.value = 1
              s.out_fsm.val.value    = 1
              if s.in_control.msg.src0 >= nReg:
                s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1


        #=========================================================================
        # copy
        #=========================================================================
        elif s.in_control.msg.ctl == COPY:

          s.go.value = 1

          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0[0]].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
            else:
              s.go.value = 0
      
          # compute
          s.des_tmp.value = s.src0_tmp


          # output
          if s.in_control.msg.des[nLogReg]: # output to right neighbor
            s.out_neighbor[0].msg.value = s.des_tmp
            if not s.out_neighbor[0].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 1]: # output to left neighbor
            s.out_neighbor[1].msg.value = s.des_tmp
            if not s.out_neighbor[1].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 2]: # write to local RF
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp  

          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1
            
            if s.in_control.msg.des[nLogReg]:
              s.out_neighbor[0].val.value = 1
            if s.in_control.msg.des[nLogReg + 1]:
              s.out_neighbor[1].val.value = 1
            if s.in_control.msg.des[nLogReg + 2]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # DEC
        #=========================================================================
        elif s.in_control.msg.ctl == DEC:

          s.go.value = 1

          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0[0]].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
            else:
              s.go.value = 0
      
          # compute
          s.des_tmp.value = s.src0_tmp - 1


          # output
          if s.in_control.msg.des[nLogReg]: # output to right neighbor
            s.out_neighbor[0].msg.value = s.des_tmp
            if not s.out_neighbor[0].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 1]: # output to left neighbor
            s.out_neighbor[1].msg.value = s.des_tmp
            if not s.out_neighbor[1].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 2]: # write to local RF
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp  

          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1
            
            if s.in_control.msg.des[nLogReg]:
              s.out_neighbor[0].val.value = 1
            if s.in_control.msg.des[nLogReg + 1]:
              s.out_neighbor[1].val.value = 1
            if s.in_control.msg.des[nLogReg + 2]:
              s.rf.wr_en.value = 1


        #=========================================================================
        # two-operand arithmetic
        #=========================================================================
        elif (s.in_control.msg.ctl == SUB)\
              or (s.in_control.msg.ctl == ADD)\
              or (s.in_control.msg.ctl == MUL):

          s.go.value = 1

          # src0
          if s.in_control.msg.src0 < nReg:
            s.rf.rd_addr[0].value  = s.in_control.msg.src0
            s.src0_tmp.value       = s.rf.rd_data[0]

          elif s.in_control.msg.src0 >= nReg:
            if s.in_neighbor[s.in_control.msg.src0[0]].val:
              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
            else:
              s.go.value = 0
      
            
          # src1
          if s.in_control.msg.src1 < nReg:
            s.rf.rd_addr[1].value  = s.in_control.msg.src1
            s.src1_tmp.value       = s.rf.rd_data[1]

          elif s.in_control.msg.src1 >= nReg:
            if s.in_neighbor[s.in_control.msg.src1[0]].val:
              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1[0]].msg
            else:
              s.go.value = 0

          # compute
          if s.in_control.msg.ctl == SUB:
            s.des_tmp.value = s.src0_tmp - s.src1_tmp
          elif s.in_control.msg.ctl == ADD:
            s.des_tmp.value = s.src0_tmp + s.src1_tmp
          elif s.in_control.msg.ctl == MUL:
            s.des_tmp.value = s.src0_tmp * s.src1_tmp


          # output
          if s.in_control.msg.des[nLogReg]: # output to right neighbor
            s.out_neighbor[0].msg.value = s.des_tmp
            if not s.out_neighbor[0].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 1]: # output to left neighbor
            s.out_neighbor[1].msg.value = s.des_tmp
            if not s.out_neighbor[1].rdy: s.go.value = 0

          if s.in_control.msg.des[nLogReg + 2]: # write to local RF
            s.rf.wr_addr.value = s.in_control.msg.des[0:nLogReg]
            s.rf.wr_data.value = s.des_tmp  

          # set control signals
          if s.go:
            s.in_control.rdy.value = 1
            if s.in_control.msg.src0 >= nReg:
              s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1
            if s.in_control.msg.src1 >= nReg:
              s.in_neighbor[s.in_control.msg.src1[0]].rdy.value = 1
            
            if s.in_control.msg.des[nLogReg]:
              s.out_neighbor[0].val.value = 1
            if s.in_control.msg.des[nLogReg + 1]:
              s.out_neighbor[1].val.value = 1
            if s.in_control.msg.des[nLogReg + 2]:
              s.rf.wr_en.value = 1


######################################## MAYANK ############################################
#
#
#        #=========================================================================
#        # two-operand arithmetic - SWAP
#        #=========================================================================
#        elif (s.in_control.msg.ctl == SWAP):
#
#          s.go.value = 1
#
#          # src0
#          if s.in_control.msg.src0 < nReg:
#            s.rf.rd_addr[0].value  = s.in_control.msg.src0
#            s.src0_tmp.value       = s.rf.rd_data[0]
#
#          elif s.in_control.msg.src0 >= nReg:
#            if s.in_neighbor[s.in_control.msg.src0[0]].val:
#              s.src0_tmp.value = s.in_neighbor[s.in_control.msg.src0[0]].msg
#            else:
#              s.go.value = 0
#      
#            
#          # src1
#          if s.in_control.msg.src1 < nReg:
#            s.rf.rd_addr[1].value  = s.in_control.msg.src1
#            s.src1_tmp.value       = s.rf.rd_data[1]
#
#          elif s.in_control.msg.src1 >= nReg:
#            if s.in_neighbor[s.in_control.msg.src1[0]].val:
#              s.src1_tmp.value = s.in_neighbor[s.in_control.msg.src1[0]].msg
#            else:
#              s.go.value = 0
#       
#
#          # output
#          if s.in_control.msg.des[nLogReg]: # output to right neighbor
#            s.out_neighbor[0].msg.value = s.src0_tmp
#            if not s.out_neighbor[0].rdy: s.go.value = 0
#
#          if s.in_control.msg.des[nLogReg + 1]: # output to left neighbor
#            s.out_neighbor[1].msg.value = s.src0_tmp
#            if not s.out_neighbor[1].rdy: s.go.value = 0
#
#          if s.in_control.msg.des[nLogReg + 2]: # write to local RF
#            s.rf.wr_addr[0].value = s.in_control.msg.des[0:nLogReg]
#            s.rf.wr_data[0].value = s.src1_tmp
#            s.rf.wr_addr[1].value = s.in_control.msg.des[5:7]
#            s.rf.wr_data[1].value = s.src0_tmp  
#
#          # set control signals
#          if s.go:
#            s.in_control.rdy.value = 1
#            if s.in_control.msg.src0 >= nReg:
#              s.in_neighbor[s.in_control.msg.src0[0]].rdy.value = 1
#            if s.in_control.msg.src1 >= nReg:
#              s.in_neighbor[s.in_control.msg.src1[0]].rdy.value = 1
#            
#            if s.in_control.msg.des[nLogReg]:
#              s.out_neighbor[0].val.value = 1
#            if s.in_control.msg.des[nLogReg + 1]:
#              s.out_neighbor[1].val.value = 1
#            if s.in_control.msg.des[nLogReg + 2]:
#              s.rf.wr_en[0].value = 1
#              s.rf.wr_en[1].value = 1



  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    inst2char = {
      0 : "LD ",
      1 : "ST ",
      2 : "CGT",
      3 : "SUB",
      4 : "CEZ",
      5 : "ADD",
      6 : "MUL",
      7 : "CPY",
      8 : "DEC",
      9 : "SWP",
    }

    if s.in_control.rdy:
      s.inst_str = inst2char[s.in_control.msg.ctl.uint()]
    else: s.inst_str = "#  "
    s.rf.rd_addr[0].value = 0
    s.rf.rd_addr[1].value = 1
    #return " {} | {} > {} | {} > {} | {} > {} | {} " \
    #  .format( s.inst_str, s.in_mem, s.out_mem, s.in_neighbor[0], s.out_neighbor[0], s.in_neighbor[1], s.out_neighbor[1], s.out_fsm)

    # simpler line trace
    return " {} | {} | {} " .format( s.inst_str, s.rf.rd_data[0], s.rf.rd_data[1] )


