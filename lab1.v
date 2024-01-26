module lab1_FSM(
	input wire clk, 
	input wire rst,
	input wire fifty,
	input wire dollar,
	input wire cancel,
	output reg[1:0] st,
	output reg insertCoin,
	output reg moneyReturn,
	output reg dispense
);

parameter INIT = 0, FIFTY = 1, VEND = 2, RETURN = 3;

reg [1:0] nst = INIT;

always @ (posedge clk) begin
    st = nst;
    if(rst)begin
        st = INIT;
    end
end

always @ * begin
    case(st)
        INIT: begin
            if(dollar) nst = VEND;
            if(fifty) nst = FIFTY;
            insertCoin = 1'b1;
        end
        FIFTY: begin
            if(dollar) nst = RETURN;
            if(fifty) nst = VEND;
            if(cancel) nst = RETURN;
            insertCoin = 1'b1;
        end
        VEND: begin
            dispense = 1'b1;
        end
        RETURN: begin
            nst = INIT
            moneyReturn = 1'b1;
        end
    endcase
end

endmodule