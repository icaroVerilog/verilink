import sys
import math
import re


sys.dont_write_bytecode = True



def ind(value):
    indentation = ""
    for index in range(value):
        indentation = indentation + "\t"
    return indentation

def break_line():
    return "\n";

def replace_last_occurency(string, pattern, repl):
    matches = list(re.finditer(pattern, string))
    
    if not matches:
        return string
    
    last_match = matches[-1]
    start = last_match.start()
    end = last_match.end()

    return string[:start] + repl + string[end:]

def is_positive_int(value):
    print(value)
    print(value.isdigit())
    return value.isdigit() and int(value) > 0



class ConstructGenerator:
    def generate_wire(self, name, width, cardinality=""):
        if (cardinality != ""):
            cardinality = cardinality + " "

        if (width > 1):
            return f"{cardinality}wire [{width-1}:0] {name};\n"
        else:
            return f"{cardinality}wire {name};\n"
    
    def generate_register(self, name, width, cardinality=""):
        if (cardinality != ""):
            cardinality = cardinality + " "

        if (width > 1):
            return f"{cardinality}reg [{width-1}:0] {name};\n"
        else:
            return f"{cardinality}reg {name};\n"
    
    def generate_atribution(self, l_value, r_value, type):
        return f"{l_value} {type} {r_value};"
    
    def generate_always(self, edge, body):

        if (edge == "p"):
            src = ind(1) + f"always @(posedge clk) begin\n{body}{ind(1)}end\n"

        return src

    def to_bin(self, value, num_bits):
        if value < 0:
            raise ValueError("O valor deve ser não negativo.")
        if num_bits <= 0:
            raise ValueError("O número de bits deve ser positivo.")
        
        binary = bin(value)[2:]
        
        bin_str = binary.zfill(num_bits)
        
        if len(binary) > num_bits:
            raise ValueError(f"O valor {value} não pode ser representado em {num_bits} bits.")
        
        return bin_str


class ParameterReader:
    def __init__(self):
        self.__parameters = {
            "source_bitwidth": None, 
            "destination_bitwidth": None,
            "output_bitwidth": None,
            "trigger_edge": "p"
        }

    def read(self, parameters):
        parameters.pop(0)

        eexceptions = []

        try:
            for index in range(len(parameters)):
                if (parameters[index] == "-s" and is_positive_int(parameters[index+1])):
                    self.__parameters["source_bitwidth"] = parameters[index+1]
                if (parameters[index] == "-d" and is_positive_int(parameters[index+1])):
                    self.__parameters["destination_bitwidth"] = parameters[index+1]
                if (parameters[index] == "-o" and is_positive_int(parameters[index+1])):
                    self.__parameters["output_bitwidth"] = parameters[index+1]
                if (parameters[index] == "-e"):
                    if (parameters[index+1] != "p" and parameters[index+1] != "n"):
                        print("ERRO")
                    self.__parameters["trigger_edge"] = parameters[index+1]
        except ValueError:
            pass
        return self.__parameters


        
class InterfaceGenerator(ConstructGenerator):
    def __init__(self, parameters):
        self.__buffer_qnt = math.ceil(int(parameters["source_bitwidth"]) / int(parameters["destination_bitwidth"]))
        self.__assigned_buffers = []
        self.__buffer_full = []
        self.__buffer_list = []
        self.__current_buffer = 0
        self.__counter_needed_bw = 0
        self.src_bw = int(parameters["source_bitwidth"])
        self.dest_bw = int(parameters["destination_bitwidth"])
        self.out_bw = int(parameters["output_bitwidth"])

    def execute(self):

        horizontal_board = ""
        horizontal_board += "//     \u2554"
        horizontal_board += "\u2550" * 48
        horizontal_board += "\u2557\n"
        horizontal_board += "//     \u2551  This code is licensed under the MIT License.  \u2551\n"
        horizontal_board += "//     \u2551  Modify this module according to your needs.   \u2551\n"
        horizontal_board += "//     \u255A"
        horizontal_board += "\u2550" * 48
        horizontal_board += "\u255D\n"
        horizontal_board += "\n\n"

        src = ""
        src += horizontal_board
        src += "module interface (\n"
        src += ind(1) + "clk,\n"
        src += ind(1) + "rst,\n"
        src += ind(1) + "data_in,\n"
        src += ind(1) + "data_out,\n"
        src += ind(1) + "valid_data_in,\n"
        src += ind(1) + "valid_data_out\n"
        src += ");"


        src += break_line()
        src += ind(1) + generator.generate_wire("clk", 1, "input")
        src += ind(1) + generator.generate_wire("rst", 1, "input")
        src += ind(1) + generator.generate_wire("valid_data_in", 1, "input")
        src += ind(1) + generator.generate_wire("data_in", self.src_bw, "input")
        src += break_line()
        src += ind(1) + generator.generate_wire("data_out", self.out_bw * self.__buffer_qnt, "output")
        src += ind(1) + generator.generate_wire("valid_data_out", self.__buffer_qnt, "output")
        src += break_line()


        if (self.__buffer_qnt == 1):
            src += ind(1) + generator.generate_register("buffer", int(parameters["destination_bitwidth"]), "")
        else:
            for index in range(self.__buffer_qnt):
                src += ind(1) + generator.generate_register(f"buffer{index}", int(parameters["destination_bitwidth"]), "")

        if (self.src_bw % self.dest_bw != 0):
            src += ind(1) + generator.generate_register(f"buffer_aux", int(parameters["destination_bitwidth"]), "")
        src += break_line()
        src += ind(1) + generator.generate_register("valid_data", self.__buffer_qnt)
        src += ind(1) + "`"
        if (self.src_bw < self.dest_bw):
            src += ind(1) + generator.generate_register("state", 16)
        src += break_line()
        src += self.generate_always("p")
        src = src.replace("`",generator.generate_register("counter", self.__counter_needed_bw))


        src += "endmodule"
        return src
    
    def __buffers_already_assigned(self):
        assigned = self.__assigned_buffers
        buffers = self.__buffer_list

        assigned.sort()
        buffers.sort()

        if (assigned == buffers):
            return True
        else:
            return False

    def __get_buffer(self):
        if (self.__current_buffer == len(self.__buffer_list)):
            self.__current_buffer = 0
        buffer = self.__buffer_list[self.__current_buffer]
        self.__current_buffer = self.__current_buffer + 1
        return buffer

    def __verify_stop_condition(self, conf_possibilities):
        if (len(conf_possibilities) > 1):
            first:list = conf_possibilities[0]   
            last:list = conf_possibilities[len(conf_possibilities) - 1]

            for index in range(len(first)):
                if (first[index][1] != last[index][1]):
                    return False
            return True
        else:
            return False

    def __needed_bit_quantity(self, value):
        if value < 0:
            return 0 
        if value == 0:
            return 1
        return math.floor(math.log2(value)) + 1

    def generate_buffer_assignment(self):
        conf_possibilities = []
        max_bits = 0
        p = 0

        for index in range(self.__buffer_qnt):
            self.__buffer_list.append(index)
            self.__buffer_full.append(0)
        while (True):
            max_bits = self.src_bw
            iteration = []
            while (True):
                if (max_bits > self.dest_bw):
                    if (p > 0):
                        pair = []
                        pair.append(self.__get_buffer())
                        pair.append(p)
                        iteration.append(pair)
                        max_bits = max_bits - p
                        p = 0
                    else:
                        pair = []
                        pair.append(self.__get_buffer())
                        pair.append(self.dest_bw)
                        iteration.append(pair)
                        max_bits = max_bits - self.dest_bw
                elif (max_bits == self.dest_bw):
                    pair = []
                    pair.append(self.__get_buffer())
                    pair.append(max_bits)
                    iteration.append(pair)
                    max_bits = 0

                    break
                elif (max_bits < self.dest_bw):
                    pair = []
                    pair.append(self.__get_buffer())
                    pair.append(max_bits)
                    iteration.append(pair)
                    p = self.dest_bw - max_bits

                    break
            conf_possibilities.append(iteration)

            if (iteration[len(iteration) - 1][1] != self.dest_bw):
                self.__current_buffer = iteration[len(iteration) - 1][0]

            if (self.__verify_stop_condition(conf_possibilities)):
                conf_possibilities.pop()
                break

        conditional_structure_counter = 0
        src = ""

        carry = 0
        simple_carry = 0
        carry_lower_bit = 0

        for conf in conf_possibilities:
            needed_bit_quantity = self.__needed_bit_quantity(len(conf_possibilities) - 1)

            self.__counter_needed_bw = needed_bit_quantity

            binary_value = generator.to_bin(
                conditional_structure_counter, 
                needed_bit_quantity
            )

            src += ind(3) + f"if (counter == {needed_bit_quantity}'b{binary_value}) begin\n"
            lower_bit = 0
            upper_bit = 0
            for index in range(len(conf)):
                if (carry == 0):
                    upper_bit = (lower_bit + conf[index][1]) - 1
                    if (self.__buffers_already_assigned()):
                        src += ind(4) + f"buffer_aux <= data_in[{upper_bit}:{lower_bit}];\n"
                        carry = upper_bit - lower_bit
                        carry_lower_bit = lower_bit
                    else:
                        if (simple_carry != 0):
                            src += ind(4) + f"buffer{conf[index][0]}[{self.dest_bw - 1}:{simple_carry}] <= data_in[{upper_bit}:{lower_bit}];\n"
                            simple_carry = 0
                        else:
                            src += ind(4) + f"buffer{conf[index][0]} <= data_in[{upper_bit}:{lower_bit}];\n"
                        
                        if (((upper_bit - lower_bit + 1) != self.dest_bw) and (index == len(conf) - 1)):
                            simple_carry = upper_bit - lower_bit + 1
                        self.__assigned_buffers.append(conf[index][0])
                    lower_bit = upper_bit + 1
                else:
                    upper_bit = (lower_bit + conf[index][1]) - 1
                    if (self.__buffers_already_assigned()):
                        src += ind(4) + f"buffer_aux <= data_in[{upper_bit}:{lower_bit}];\n"
                        carry = upper_bit - lower_bit
                        carry_lower_bit = lower_bit
                    else:
                        carry_lower_bit = 0
                        src += ind(4) + f"buffer{conf[index][0]} <= {{buffer_aux[{carry_lower_bit + carry}:{carry_lower_bit}], data_in[{upper_bit}:{lower_bit}]}};\n"
                        carry = 0
                    lower_bit = upper_bit + 1
                self.__buffer_full[conf[index][0]] = self.__buffer_full[conf[index][0]] + conf[index][1]
            
            valid_data_conf = ""
            for index in range(self.__buffer_qnt):
                if (self.__buffer_full[index] >= self.dest_bw):
                    valid_data_conf = valid_data_conf + "1"
                    self.__buffer_full[index] = self.__buffer_full[index] - self.dest_bw
                else:
                    valid_data_conf = valid_data_conf + "0"
            src += ind(4) + f"valid_data <= {self.__buffer_qnt}'b{valid_data_conf};\n"


            self.__assigned_buffers = []
            

            conditional_structure_counter = conditional_structure_counter + 1

            if(conditional_structure_counter == len(conf_possibilities)):
                src += ind(4) + f"counter <= {needed_bit_quantity}'b{generator.to_bin(0, needed_bit_quantity)};\n"
            else:
                src += ind(4) + "counter <= counter + 1'b1;\n"     

            src += ind(3) + "end\n" 
        return src

    # This method assigns the buffer when the source is smaller than destination
    def generate_buffer_assignment2(self):
        states = []

        buffer_aux_carry = 0

        max_counter_value = math.ceil(self.dest_bw / self.src_bw)
        # counter_bw = self.__needed_bit_quantity(max_counter_value)
        counter_bw = 16

        state = 0

        first_iteration = True
        finish = False
        first_conf = [None, None, None]

        while(finish == False):

            data_in_upper_bit = self.src_bw - 1
            data_in_lower_bit = 0
            buffer_upper_bit = self.dest_bw - 1
            buffer_lower_bit = self.dest_bw - self.src_bw


            valid_data = False
            counter = 0
            
            src = ind(3) + f"if (state == 16'b{generator.to_bin(state, 16)}) begin\n"
            while(valid_data == False):
                src += ind(4) + f"if (counter == {counter_bw}'b{generator.to_bin(counter, counter_bw)}) begin\n"
                if (counter == 0):
                    src += ind(5) + "valid_data <= 1'b0;\n"


                if (buffer_aux_carry != 0):
                    buffer_lower_bit = buffer_lower_bit - buffer_aux_carry
                    
                    if (buffer_lower_bit < 0):
                        buffer_lower_bit = 0

                    if (self.src_bw + buffer_aux_carry > self.dest_bw):
                        src += ind(5) + f"buffer[{buffer_upper_bit}:{buffer_lower_bit}] <= {{buffer_aux[{buffer_aux_carry - 1}:{0}], data_in[{data_in_upper_bit}:{self.src_bw - buffer_aux_carry}]}};\n"
                        src += ind(5) + f"buffer_aux <= data_in[{self.src_bw - buffer_aux_carry - 1}:{0}];\n"
                        buffer_aux_carry = self.src_bw - buffer_aux_carry


                    else:
                        src += ind(5) + f"buffer[{buffer_upper_bit}:{buffer_lower_bit}] <= {{buffer_aux[{buffer_aux_carry - 1}:{0}], data_in}};\n"
                        buffer_aux_carry = 0
                else:
                    if (buffer_lower_bit < 0):
                        buffer_lower_bit = 0

                    if (data_in_upper_bit == self.src_bw - 1 and data_in_lower_bit == 0):
                        src += ind(5) + f"buffer[{buffer_upper_bit}:{buffer_lower_bit}] <= data_in;\n"
                    else:
                        src += ind(5) + f"buffer[{buffer_upper_bit}:{buffer_lower_bit}] <= data_in[{data_in_upper_bit}:{data_in_lower_bit}];\n"
                        data_in_upper_bit = data_in_lower_bit - 1
                        src += ind(5) + f"buffer_aux <= data_in[{data_in_upper_bit}:{0}];\n"
                        buffer_aux_carry = data_in_upper_bit + 1

                if (buffer_lower_bit <= 0):
                    state = state + 1

                    src += ind(5) + "valid_data <= 1'b1;\n"
                    src += ind(5) + f"counter <= {counter_bw}'b{generator.to_bin(0, counter_bw)};\n"
                    src += ind(5) + f"state <= 16'b{generator.to_bin(state, 16)};\n"
                    valid_data = True
                else:
                    src += ind(5) + "counter <= counter + 1'b1;\n"
                    counter = counter + 1
                

                if (first_iteration == True):
                    first_iteration = False
                    first_conf = [buffer_upper_bit, buffer_lower_bit, buffer_aux_carry]
                elif (
                    first_conf[0] == buffer_upper_bit and 
                    first_conf[1] == buffer_lower_bit and 
                    first_conf[2] == buffer_aux_carry
                ):
                    finish = True

                buffer_upper_bit = buffer_lower_bit - 1
                buffer_lower_bit = buffer_upper_bit - self.src_bw

                if (buffer_lower_bit < 0):
                    buffer_lower_bit = 0

                data_in_lower_bit = data_in_upper_bit - buffer_upper_bit

                if (data_in_lower_bit < 0):
                    data_in_lower_bit = 0

                src += ind(4) + "end\n"
            src += ind(3) + "end\n"
            states.append(src)

        states.pop()
        src = ""

        states[len(states) - 1] = replace_last_occurency(
            states[len(states) - 1], 
                r"(16'b[0|1]+)", 
                "16'b0000000000000000"
            )

        for state in states:
            src += state
    
        return src

    def generate_always(self, edge):
        if (edge == "p"):
            src = ind(1) + f"always @(posedge clk) begin\nx\n{ind(1)}end\n"
        elif (edge == "n"):
            src = ind(1) + f"always @(negedge clk) begin\nx\n{ind(1)}end\n"

        always_src = ind(2) + f"if (rst) begin\n"

        if (self.src_bw >= self.dest_bw):
            for index in range(self.__buffer_qnt):
                always_src += ind(3) + f"buffer{index} <= {self.dest_bw}'b{generator.to_bin(0, self.dest_bw)};\n"
        else:
            always_src += ind(3) + f"buffer <= {self.dest_bw}'b{generator.to_bin(0, self.dest_bw)};\n"

        if (self.src_bw % self.dest_bw != 0):
            always_src += ind(3) + f"buffer_aux <= {self.dest_bw}'b{generator.to_bin(0, self.dest_bw)};\n"
        always_src += ind(3) + f"valid_data <= {self.__buffer_qnt}'b{generator.to_bin(0, self.__buffer_qnt)};\n"

        always_src += ind(3) + f"counter <= ç'b`;\n"

        if (self.src_bw < self.dest_bw):
            always_src += ind(3) + f"state <= {16}'b{generator.to_bin(0, 16)};\n"

        always_src += ind(2) + "end\n"
        always_src += ind(2) + "else if (valid_data_in) begin\n"

        if (self.src_bw >= self.dest_bw):
            always_src += self.generate_buffer_assignment()
        else:
            always_src += self.generate_buffer_assignment2()
            self.__counter_needed_bw = 16
        always_src = always_src.replace("ç",str(self.__counter_needed_bw))
        always_src = always_src.replace("`",str(generator.to_bin(0, self.__counter_needed_bw)))
        always_src += ind(2) + "end"
        src = src.replace("x", always_src)
        return src

parameter_reader = ParameterReader()
generator = ConstructGenerator()

parameters = parameter_reader.read(sys.argv)

interfaceGenerator = InterfaceGenerator(parameters)
src = interfaceGenerator.execute()


with open("interface.v", "w", encoding="utf-8") as arquivo:
    arquivo.write(src)
