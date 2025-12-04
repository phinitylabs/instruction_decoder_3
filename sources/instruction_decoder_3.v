`timescale 1ns/1ps
module instruction_decoder_3(
    input wire [2:0] id,             
    input wire [4:0] instr_in,
    input wire cc_in,
    input wire instr_en,
    output reg cen, 
    output reg rst, 
    output reg oen, 
    output reg inc, 
    output reg rsel, 
    output reg rce,  
    output reg pc_mux_sel, 
    output reg [1:0] a_mux_sel, 
    output reg [1:0] b_mux_sel, 
    output reg push,
    output reg pop, 
    output reg src_sel,
    output reg stack_we,
    output reg stack_re,
    output reg out_ce
);
always @(*) begin : instruction_decoder
    // --------------------------------------
    // If ID != 011 → decoder is disabled
    // --------------------------------------
    if (id != 3'b011) begin
        rst         = 1'b0;
        out_ce      = 1'b0;
        rsel        = 1'b0; 
        rce         = 1'b0; 
        cen         = 1'b0; 
        stack_re    = 1'b0; 
        pop         = 1'b0;
        a_mux_sel   = 2'b10;
        b_mux_sel   = 2'b10;
        oen         = 1'b0; 
        pc_mux_sel  = 1'b0; 
        inc         = 1'b0; 
        src_sel     = 1'b0;
        push        = 1'b0;
        stack_we    = 1'b0;
    end
    // --------------------------------------
    // ID == 011 → normal decoder operation
    // --------------------------------------
    else begin
        casex({instr_in, cc_in, instr_en})
         7'b0110101 : begin   // Instruction Disable
                        rst        = 1'b0;
                        out_ce     = 1'b0;
                        rsel       = 1'b0;
                        rce        = 1'b0;
                        cen        = 1'b0;
                        stack_re   = 1'b0;
                        pop        = 1'b0;
                        a_mux_sel  = 2'b10;
                        b_mux_sel  = 2'b10;
                        oen        = 1'b1;
                        pc_mux_sel = 1'b0;
                        inc        = 1'b0;
                        src_sel    = 1'b0;
                        push       = 1'b0;
                        stack_we   = 1'b0;
                      end
         7'b01100x0 : begin  // PUSH D
                        rst         = 1'b0;
                        out_ce      = 1'b0;
                        rsel        = 1'b0;
                        rce         = 1'b1;
                        cen         = 1'b0; 
                        stack_re    = 1'b0; 
                        pop         = 1'b0;
                        a_mux_sel   = 2'b10; 
                        b_mux_sel   = 2'b00; 
                        oen         = 1'b1; 
                        pc_mux_sel  = 1'b1; 
                        inc         = 1'b1; 
                        src_sel     = 1'b1; 
                        push        = 1'b1; 
                        stack_we    = 1'b1; 
                      end
         7'b01101x0 : begin  // POP S
                        rst         = 1'b0;
                        out_ce      = 1'b0;
                        rsel        = 1'b0;
                        rce         = 1'b1;
                        cen         = 1'b0; 
                        stack_re    = 1'b1; 
                        pop         = 1'b1; 
                        a_mux_sel   = 2'b10; 
                        b_mux_sel   = 2'b01; 
                        oen         = 1'b1; 
                        pc_mux_sel  = 1'b1; 
                        inc         = 1'b1; 
                        src_sel     = 1'b0; 
                        push        = 1'b0; 
                        stack_we    = 1'b0; 
                      end    
         7'b01110x0 : begin  // POP PC
                        rst         = 1'b0;
                        out_ce      = 1'b0;
                        rsel        = 1'b0;
                        rce         = 1'b1;
                        cen         = 1'b0; 
                        stack_re    = 1'b1; 
                        pop         = 1'b1; 
                        a_mux_sel   = 2'b10; 
                        b_mux_sel   = 2'b01; 
                        oen         = 1'b1; 
                        pc_mux_sel  = 1'b1; 
                        inc         = 1'b1; 
                        src_sel     = 1'b0; 
                        push        = 1'b0; 
                        stack_we    = 1'b0; 
                      end    
         7'b01111x0 : begin  // HOLD PC
                        rst         = 1'b0;
                        out_ce      = 1'b0;
                        rsel        = 1'b0;
                        rce         = 1'b1;
                        cen         = 1'b0; 
                        stack_re    = 1'b0; 
                        pop         = 1'b0; 
                        a_mux_sel   = 2'b10; 
                        b_mux_sel   = 2'b00; 
                        oen         = 1'b1; 
                        pc_mux_sel  = 1'b1; 
                        inc         = 1'b0; 
                        src_sel     = 1'b0; 
                        push        = 1'b0; 
                        stack_we    = 1'b0; 
                      end
            default : begin
                        rst         = 1'b0;
                        out_ce      = 1'b0;
                        rsel        = 1'b0; 
                        rce         = 1'b0; 
                        cen         = 1'b0; 
                        stack_re    = 1'b0; 
                        pop         = 1'b0;
                        a_mux_sel   = 2'b10;
                        b_mux_sel   = 2'b10;
                        oen         = 1'b0; 
                        pc_mux_sel  = 1'b0; 
                        inc         = 1'b0; 
                        src_sel     = 1'b0;
                        push        = 1'b0;
                        stack_we    = 1'b0;
                      end
            endcase
        end
    end
endmodule
