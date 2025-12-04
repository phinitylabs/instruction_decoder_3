import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

# ------------------------------------------------------------
# Helper: check outputs
# ------------------------------------------------------------
async def check_outputs(dut, exp, label=""):
    await Timer(1, units="ns")

    for signal, expected in exp.items():
        actual = int(getattr(dut, signal).value)
        assert actual == expected, (
            f"{label}: {signal} expected {expected}, got {actual}"
        )


# ------------------------------------------------------------
# Test 0 – Decoder disabled when ID != 010
# ------------------------------------------------------------
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

    await check_outputs(dut, expected, "Decoder disabled (ID!=010)")


# ------------------------------------------------------------
# Helper: execute instruction with ID=010
# ------------------------------------------------------------
async def run_instr(dut, instr, cc, en, expected, label):
    dut.id.value = 0b010
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en

    await Timer(2, units="ns")
    await check_outputs(dut, expected, label)


# ------------------------------------------------------------
# Test 1 – Instruction Disable: 7'b0110101
# instr_in = 01101  (0x0D)
# cc_in    = 0
# instr_en = 1
# ------------------------------------------------------------
@cocotb.test()
async def test_instruction_disable(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b01101,
        cc=0,
        en=1,
        expected=expected,
        label="Instruction Disable 0110101"
    )


# ------------------------------------------------------------
# Test 2 – PUSH D: pattern 7'b01100x0 → instr_in=01100, en=0
# ------------------------------------------------------------
@cocotb.test()
async def test_push_d(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":1, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b01100,
        cc=0,
        en=0,
        expected=expected,
        label="PUSH D (01100x0)"
    )


# ------------------------------------------------------------
# Test 3 – POP S: pattern 7'b01101x0
# ------------------------------------------------------------
@cocotb.test()
async def test_pop_s(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":1,
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b01101,
        cc=0,
        en=0,
        expected=expected,
        label="POP S (01101x0)"
    )


@cocotb.test()
async def test_pop_pc(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":0,  
        "oen":1, "pc_mux_sel":1, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b01110,
        cc=0,
        en=0,
        expected=expected,
        label="POP PC (01110x0)"
    )


# ------------------------------------------------------------
# Test 5 – HOLD PC: pattern 7'b01111x0
# ------------------------------------------------------------
@cocotb.test()
async def test_hold_pc(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":1, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b01111,
        cc=0,
        en=0,
        expected=expected,
        label="HOLD PC (01111x0)"
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
