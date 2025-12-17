import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

async def check_outputs(dut, exp, label=""):
    await Timer(1, units="ns")
    for signal, expected in exp.items():
        actual = int(getattr(dut, signal).value)
        assert actual == expected, (
            f"{label}: {signal} expected={expected}, got={actual}"
        )


@cocotb.test()
async def test_id_disable(dut):
    dut.id.value = 0b000
    dut.instr_in.value = 0
    dut.cc_in.value = 0
    dut.instr_en.value = 0

    await Timer(2, units="ns")

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":0, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await check_outputs(dut, expected, "Decoder disabled (ID!=011)")


async def run_instr(dut, instr, cc, en, expected, label):
    dut.id.value = 0b011
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en
    await Timer(2, units="ns")
    await check_outputs(dut, expected, label)


@cocotb.test()
async def test_instruction_disable(dut):
    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(dut, 0b01101, 0, 1, expected, "Instruction Disable")


@cocotb.test()
async def test_push_d(dut):
    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":1, "push":1, "stack_we":1
    }
    await run_instr(dut, 0b01100, 0, 0, expected, "PUSH D")


@cocotb.test()
async def test_pop_s(dut):
    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":1,
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }
    await run_instr(dut, 0b01101, 0, 0, expected, "POP S")


@cocotb.test()
async def test_pop_pc(dut):
    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":1,
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }
    await run_instr(dut, 0b01110, 0, 0, expected, "POP PC")


@cocotb.test()
async def test_hold_pc(dut):
    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":1, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }
    await run_instr(dut, 0b01111, 0, 0, expected, "HOLD PC")


EXP_INVALID_ID = dict(
    rst=0, out_ce=0, rsel=0, rce=0, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=2,
    oen=0, pc_mux_sel=0, inc=0,
    src_sel=0, push=0, stack_we=0
)

EXP_DEFAULT = EXP_INVALID_ID.copy()

EXP_INSTR_DISABLE = dict(
    rst=0, out_ce=0, rsel=0, rce=0, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=2,
    oen=1, pc_mux_sel=0, inc=0,
    src_sel=0, push=0, stack_we=0
)


async def check_invalid_id(dut, id_val):
    dut.id.value = id_val
    dut.instr_in.value = 0
    dut.cc_in.value = 0
    dut.instr_en.value = 0
    await Timer(1, units="ns")

    for sig, exp in EXP_INVALID_ID.items():
        assert int(getattr(dut, sig).value) == exp, (
            f"Invalid ID {id_val:03b}: {sig} mismatch"
        )

@cocotb.test() 
async def test_invalid_id_000(dut): 
   await check_invalid_id(dut, 0b000)
@cocotb.test() 
async def test_invalid_id_001(dut): 
   await check_invalid_id(dut, 0b001)
@cocotb.test() 
async def test_invalid_id_010(dut): 
   await check_invalid_id(dut, 0b010)
@cocotb.test() 
async def test_invalid_id_100(dut): 
   await check_invalid_id(dut, 0b100)
@cocotb.test() 
async def test_invalid_id_101(dut): 
   await check_invalid_id(dut, 0b101)
@cocotb.test() 
async def test_invalid_id_110(dut): 
   await check_invalid_id(dut, 0b110)
@cocotb.test() 
async def test_invalid_id_111(dut): 
   await check_invalid_id(dut, 0b111)


@cocotb.test()
async def test_default_case(dut):
    dut.id.value = 0b011
    dut.instr_en.value = 0
    dut.instr_in.value = 0b11111
    dut.cc_in.value = 1
    await Timer(1, units="ns")

    for sig, exp in EXP_DEFAULT.items():
        assert int(getattr(dut, sig).value) == exp


@cocotb.test()
async def invariant_instr_disable(dut):
    dut.id.value = 0b011

    # First sample
    dut.instr_in.value = 0b01101
    dut.cc_in.value = 0
    dut.instr_en.value = 1
    await Timer(1, units="ns")

    reference = {k: int(getattr(dut, k).value)
                 for k in EXP_INSTR_DISABLE}

    # Re-apply same opcode multiple times (temporal stability)
    for _ in range(5):
        await Timer(1, units="ns")
        snap = {k: int(getattr(dut, k).value)
                for k in EXP_INSTR_DISABLE}
        assert snap == reference, "Instruction-disable not stable over time"



async def invariant_cc_independent(dut, instr, sigs):
    dut.id.value = 0b011
    dut.instr_en.value = 0
    dut.instr_in.value = instr

    ref = None
    for cc in (0, 1):
        dut.cc_in.value = cc
        await Timer(1, units="ns")

        snap = {k: int(getattr(dut, k).value) for k in sigs}
        if ref is None:
            ref = snap
        else:
            assert snap == ref, f"CC dependence detected instr={instr:05b}"


@cocotb.test()
async def invariant_push_d_cc(dut):
    await invariant_cc_independent(dut, 0b01100, EXP_DEFAULT.keys())

@cocotb.test()
async def invariant_pop_s_cc(dut):
    await invariant_cc_independent(dut, 0b01101, EXP_DEFAULT.keys())

@cocotb.test()
async def invariant_pop_pc_cc(dut):
    await invariant_cc_independent(dut, 0b01110, EXP_DEFAULT.keys())

@cocotb.test()
async def invariant_hold_pc_cc(dut):
    await invariant_cc_independent(dut, 0b01111, EXP_DEFAULT.keys())


@cocotb.test()
async def invariant_default_class(dut):
    dut.id.value = 0b011
    dut.instr_en.value = 0

    ref = None
    for instr in range(32):
        if instr in (0b01100, 0b01101, 0b01110, 0b01111):
            continue
        for cc in (0, 1):
            dut.instr_in.value = instr
            dut.cc_in.value = cc
            await Timer(1, units="ns")

            snap = {k: int(getattr(dut, k).value)
                    for k in EXP_DEFAULT}

            if ref is None:
                ref = snap
            else:
                assert snap == ref, (
                    f"default invariant violated instr={instr:05b}"
                )

def test_instruction_decoder_3_hidden_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [proj_path / "sources/instruction_decoder_3.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="instruction_decoder_3",
        always=True,
    )
    runner.test(hdl_toplevel="instruction_decoder_3", test_module="test_instruction_decoder_3_hidden")
