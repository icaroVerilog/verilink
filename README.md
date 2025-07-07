# Verilink


Verilink is an open-source project designed to generate interfaces between Verilog modules in order to maximize the utilization of input bits, thereby avoiding the underuse of data transfer resources, which are often the main limiting factor in most devices. Fully modular in design, it allows the creation of a modular interface that efficiently transfers data from a source with a larger bit width to multiple destinations that use a smaller bit width.


## Architecture 

For a given input bit width, the software calculates how many outputs with the specified output bit width can be fed. In the image below, a use case is shown where the input has 16 bits, but the module being fed requires only 10 bits. This would normally result in 6 bits being underutilized. In this case, the interface stores those bits so that they can be used by another instance. To address this issue, buffers are used to store the data received by the interface, allowing it to manage and distribute the data among instances of the original circuit modules. This reduces the number of clock cycles needed to process a given amount of data, thereby increasing the circuit’s throughput.


![Interface Architecture Diagram](https://github.com/icaroVerilog/VeriLink/blob/main/images/architecture.png)

When the circuit need more bits than can be feeded in each clock cycle,  instead of memory underutilization, in this scneraio we a have a superutilization. To solve this problem the interface module logic is changed to fill the buffer with the data of multiple clock cycles

![Interface Architecture Diagram](https://github.com/icaroVerilog/VeriLink/blob/main/images/architecture2.png)

## Utilization
Verilink requires three flags for its operation:

|      Flag      |Description                          |Value Type                         |
|----------------|-------------------------------|-----------------------------|
|-s							 |specifies the number of bits to be received by the interface module        |Integer            |
|-d          		 |specifies the number of bits to be sent to the destination modules            |Integer          |
|-o          		 |specifies the number of output bits            |Integer          |
|-e              |sets the activation edge of the module, with possible values being `p` (positive edge) and `n` (negative edge)|Character
