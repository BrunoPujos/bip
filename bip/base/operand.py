import idaapi
import idc
from ida_typeinf import tinfo_t
from ida_nalt import get_op_tinfo, set_op_tinfo, del_op_tinfo

from bip.py3compat.py3compat import *

import bip.base.biptype

class BipOpType(object):
    """
        Static class allowing to get the type of the operands as define in the
        ``ua.hpp`` file from hexrays. This is equivalent to the ``idc.o_*``
        values.
    """
    VOID        =  0 #: No Operand.
    REG         =  1 #: General Register (al,ax,es,ds...).
    MEM         =  2 #: Direct Memory Reference  (DATA).
    PHRASE      =  3 #: Memory Ref [Base Reg + Index Reg].
    DISPL       =  4 #: Memory Reg [Base Reg + Index Reg + Displacement].
    IMM         =  5 #: Immediate Value.
    FAR         =  6 #: Immediate Far Address  (CODE).
    NEAR        =  7 #: Immediate Near Address (CODE).
    IDPSPEC0    =  8 #: processor specific type.
    IDPSPEC1    =  9 #: processor specific type.
    IDPSPEC2    = 10 #: processor specific type.
    IDPSPEC3    = 11 #: processor specific type.
    IDPSPEC4    = 12 #: processor specific type.
    IDPSPEC5    = 13 #: processor specific type.
## TODO:
## x86
#o_trreg  =       ida_ua.o_idpspec0      # trace register
#o_dbreg  =       ida_ua.o_idpspec1      # debug register
#o_crreg  =       ida_ua.o_idpspec2      # control register
#o_fpreg  =       ida_ua.o_idpspec3      # floating point register
#o_mmxreg  =      ida_ua.o_idpspec4      # mmx register
#o_xmmreg  =      ida_ua.o_idpspec5      # xmm register
#
## arm
#o_reglist  =     ida_ua.o_idpspec1      # Register list (for LDM/STM)
#o_creglist  =    ida_ua.o_idpspec2      # Coprocessor register list (for CDP)
#o_creg  =        ida_ua.o_idpspec3      # Coprocessor register (for LDC/STC)
#o_fpreglist  =   ida_ua.o_idpspec4      # Floating point register list
#o_text  =        ida_ua.o_idpspec5      # Arbitrary text stored in the operand
#o_cond  =        (ida_ua.o_idpspec5+1)  # ARM condition as an operand
#
## ppc
#o_spr  =         ida_ua.o_idpspec0      # Special purpose register
#o_twofpr  =      ida_ua.o_idpspec1      # Two FPRs
#o_shmbme  =      ida_ua.o_idpspec2      # SH & MB & ME
#o_crf  =         ida_ua.o_idpspec3      # crfield      x.reg
#o_crb  =         ida_ua.o_idpspec4      # crbit        x.reg
#o_dcr  =         ida_ua.o_idpspec5      # Device control register

class BipDestOpType(object):
    """
        Static class representing an enum of the ``dt_*`` macro from IDA
        indicating the type of the operand value.

        Defined in ``ua.hpp`` in IDA.
    """
    DT_BYTE         = 0     #: 8 bit
    DT_WORD         = 1     #: 16 bit
    DT_DWORD        = 2     #: 32 bit
    DT_FLOAT        = 3     #: 4 byte
    DT_DOUBLE       = 4     #: 8 byte
    DT_TBYTE        = 5     #: variable size
    DT_PACKREAL     = 6     #: packed real format for mc68040
    DT_QWORD        = 7     #: 64 bit
    DT_BYTE16       = 8     #: 128 bit
    DT_CODE         = 9     #: ptr to code (not used?)
    DT_VOID         = 10    #: none
    DT_FWORD        = 11    #: 48 bit
    DT_BITFILD      = 12    #: bit field (mc680x0)
    DT_STRING       = 13    #: pointer to asciiz string
    DT_UNICODE      = 14    #: pointer to unicode string
    DT_LDBL         = 15    #: long double (which may be different from tbyte)
    DT_BYTE32       = 16    #: 256 bit
    DT_BYTE64       = 17    #: 512 bit


class BipOperand(object):
    """
        Class representing an operand of an instruction. This class
        should be used through :class:`BipInstr` .

        .. todo:: make test property depending of type

        .. todo:: make subclass by type of operand ?

        .. todo:: support .reg and other stuff like that

        .. todo:: hex((i.Op2.specval >> 0x10) & 0xFF) give the segment

        .. todo:: make pretty printing function if possible
    """

    def __init__(self, ins, num):
        """
            Constructor for an operand object. Should not directly use this
            constructor but should be access by using the :meth:`~BipInstr.op`
            method from :class:`BipInstr` .

            :param ins: The instruction in which this operand ins present
            :type ins: :class:`BipInstr`
            :param int num: The position of the operand in the instruction.
        """
        self.instr = ins #: Instruction containing the operand
        self.opnum = num #: The position of the operand in the instruction


    @property
    def ea(self):
        """
            Property allowing to get the address of the instruction
            containing this operand.

            :return: The address of the instruction.
            :rtype: int or long
        """
        return self.instr.ea

    @property
    def str(self):
        """
            Property allowing to get the representation of the operand as a
            string.
            Wrapper on ``idc.GetOpnd`` (old) or ``idc.print_operand`` (new) .

            :return: The representation of the operand.
            :rtype: :class:`str`
        """
        return idc.print_operand(self.ea, self.opnum)

    @property
    def _op_t(self):
        """
            Return the IDA object ``op_t`` correponding to this operand.

            :return: A swig proxy on an ``op_t`` type.
        """
        return self.instr._insn.ops[self.opnum]

    @property
    def type(self):
        """
            Property allowing to get the type of the operand. This type
            correspond to the :class:`BipOpType` value .
            Wrapper on ``idc.GetOpType`` (old) or ``idc.get_operand_type``
            (new).

            :return: The type of the operand as defined in :class:`BipOpType` .
            :rtype: int
        """
        return idc.get_operand_type(self.ea, self.opnum)

    @property
    def dtype(self):
        """
            Property which allow to get the type of the operand value. Those
            can be access through the :class:`BipDestOpType` enum.
            This is is equivalent to accessing the ``op_t.dtype`` from IDA.

            :return int: The type of the destination of the operand as defined
                in :class:`BipDestOpType`.
        """
        return self._op_t.dtype

    @property
    def type_info(self):
        """
            Property which allow to get the information on the type of the
            operand if defined. This will return an object which inherit from
            :class:`BipType` if defined or ``None`` if not.

            .. note:: By default this does not seems to be defined by IDA.

            :return: A :class:`BipType` object defined for this operand or
                ``None`` if it was not defined.
        """
        ti = tinfo_t()
        if not get_op_tinfo(ti, self.ea, self.opnum): # recuperation of the type failed
            return None
        return bip.base.biptype.BipType.from_tinfo(ti)

    @type_info.setter
    def type_info(self, value):
        """
            Setter which allow to set the information type (:class:`BipType`)
            of the operand. This is equivalent to using the
            ``Edit>Operand>Set Operand Type`` menu in IDA with an
            :class:`BipType` instead of a string.

            This will create a copy of the type provided in argument
            for avoiding problem with the IDA type system. For more
            informaiton see :class:`BipType` .

            :param value: An object which inherit from :class:`BipType` and
                will be set as the type of the current operand or a string
                which represent the C type.
            :raise TypeError: If the argument does not inherit from
                :class:`BipType` or if the .
            :raise RuntimeError: If the setting of the type is not a success
                or if it was not able to create the BipType from the string.
        """
        if isinstance(value, (str, unicode)):
            value = bip.base.biptype.BipType.from_c(value)
        if not isinstance(value, bip.base.biptype.BipType):
            raise TypeError("Operand.type_info expect a BipType object or a string representing the C type.")
        if not set_op_tinfo(self.ea, self.opnum, value._get_tinfo_copy()):
            raise RuntimeError("Fail to set the type ({}) of the operand {}".format(value, self))

    @type_info.deleter
    def type_info(self):
        """
            Deleter for removing infomarion type of the operand.
        """
        del_op_tinfo(self.ea, self.opnum)

    @property
    def _value(self):
        """
            Property allowing to get the value of an operand. Depending of the
            type of the operand this value can means different things.
            Wrapper on ``idc.get_operand_value`` (new, old one was
            ``idc.GetOperandValue``).

            .. todo::

                Look at idc.get_operand_value, somethings may need
                change here.

            :return: The value of the operand.
            :rtype: int
        """
        return idc.get_operand_value(self.ea, self.opnum)

    @property
    def value(self):
        """
            Property allowing to get the value of an operand. Depending of the
            type of the operand this value can means different things.
            For an immediate the value return as a mask apply for getting only
            the number of bytes of the asm value and not the signed extended
            returned by IDA.

            .. todo::

                Look at idc.get_operand_value, somethings may need
                change here.

            .. todo::

                Support the dtype for other things than immediate (such as
                float).

            .. todo::

                Support all of the dtype for immediate

            :return: The value of the operand.
            :rtype: int
        """
        if self.is_imm:
            dt = self.dtype
            if dt == BipDestOpType.DT_BYTE:
                return self._value & 0xFF
            elif dt == BipDestOpType.DT_WORD:
                return self._value & 0xFFFF
            elif dt == BipDestOpType.DT_DWORD:
                return self._value & 0xFFFFFFFF
            elif dt == BipDestOpType.DT_FLOAT: # TODO
                return self._value & 0xFFFFFFFF
            elif dt == BipDestOpType.DT_DOUBLE: # TODO
                return self._value & 0xFFFFFFFFFFFFFFFF
            elif dt == BipDestOpType.DT_QWORD:
                return self._value & 0xFFFFFFFFFFFFFFFF
            else: # TODO
                return self._value
        return self._value

    @property
    def reg(self):
        """
            Property allowing to get the register id number for this operand.

            For register operand this is the same as :meth:`~BipOperand.value`,
            for "phrase" and "displ" it is the register used.

            :return: The id (int) for the register use by this operand or None
                if no register is used.
        """
        if self.is_reg:
            return self.value
        elif self.type == BipOpType.PHRASE or self.type == BipOpType.DISPL:
            return self._op_t.phrase
        return None

    ######################## TEST TYPE ##########################

    @property
    def is_void(self):
        """
            Test if this object represent the fact that there is no operand.
            (``BipOpType.VOID``)
        """
        return self.type == BipOpType.VOID

    @property
    def is_reg(self):
        """
            Test if the operand represent a register. (``BipOpType.REG``)
        """
        return self.type == BipOpType.REG

    @property
    def is_memref(self):
        """
            Test if the operand is a memory reference (one of MEM, PHRASE or
            DISPL in BipOpType)
        """
        t = self.type
        return t == BipOpType.MEM or t == BipOpType.PHRASE or t == BipOpType.DISPL

    @property
    def is_imm(self):
        """
            Test if the operand is an immediate value which is **not** an
            address (BipOpType.IMM).
        """
        return self.type == BipOpType.IMM

    @property
    def is_addr(self):
        """
            Test if the operand represent an address, far or near.
            (one of FAR or NEAR in BipOpType).
        """
        t = self.type
        return t == BipOpType.FAR or t == BipOpType.NEAR

    @property
    def is_proc_specific(self):
        """
            Test if this operand is processor specific.
        """
        return self.type >= BipOpType.IDPSPEC0

    ############################# OFFSET & CHANGE TYPE ######################

    def set_offset(self, base=0):
        """
            Set this operand as being an offset.

            .. todo:: this should be a setter on a property ?

            .. todo:: doc base arg
        """
        idc.op_plain_offset(self.instr.ea, self.opnum, base)
        # TODO:the opposite is: ida_bytes.clr_op_type(self.instr.ea, self.opnum)


