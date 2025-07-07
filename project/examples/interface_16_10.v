module interface (
	clk,
	rst,
	data_in
);
	input wire clk;
	input wire rst;
	input wire [15:0] data_in;

	reg [9:0] buffer0;
	reg [9:0] buffer1;
	reg [9:0] buffer_aux;

	reg [1:0] valid_data;

	always @(posedge clk) begin
		if (rst) begin
			buffer0 <= 10'b0000000000;
			buffer1 <= 10'b0000000000;
			buffer_aux <= 10'b0000000000;
			valid_data <= 2'b00;
			counter <= 3'b000;
		end
		else begin
			if (counter == 3'b000) begin
				buffer0 <= data_in[9:0];
				buffer1 <= data_in[15:10];
				valid_data <= 2'b10;
				counter <= counter + 1'b1;
			end
			if (counter == 3'b001) begin
				buffer1[9:6] <= data_in[3:0];
				buffer0 <= data_in[13:4];
				buffer_aux <= data_in[15:14];
				valid_data <= 2'b11;
				counter <= counter + 1'b1;
			end
			if (counter == 3'b010) begin
				buffer1 <= {buffer_aux[1:0], data_in[7:0]};
				buffer0 <= data_in[15:8];
				valid_data <= 2'b01;
				counter <= counter + 1'b1;
			end
			if (counter == 3'b011) begin
				buffer0[9:8] <= data_in[1:0];
				buffer1 <= data_in[11:2];
				buffer_aux <= data_in[15:12];
				valid_data <= 2'b11;
				counter <= counter + 1'b1;
			end
			if (counter == 3'b100) begin
				buffer0 <= {buffer_aux[3:0], data_in[5:0]};
				buffer1 <= data_in[15:6];
				valid_data <= 2'b11;
				counter <= 3'b000;
			end
		end
	end
endmodule