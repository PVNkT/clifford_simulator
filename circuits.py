

# 과제에서 주어진 회로
class example_circuit:
    
    def __init__(self):
        self.num_qubit = 3

    def function(self, circ):
        circ.h(1)
        circ.h(2)
        circ.cz(0,1)
        circ.cz(1,2)
        circ.h(0)
        circ.measure(0,0)
        circ.cx(0,1)
        circ.s(1)
        circ.cx(0,1)
        circ.h(1)
        circ.measure(1,1)
        circ.h(2)
        circ.cz(1,2)
        circ.h(2)
        circ.cz(0,2)
        circ.measure(2,2)
        return circ

# 30 qubit GHZ 상태를 만드는 회로
class GHZ_circuit:

    def __init__(self):
        self.num_qubit = 30
    
    def function(self,circ):
        circ.h(0)
        for i in range(self.num_qubit-1):
            circ.cx(i,i+1)
        for i in range(self.num_qubit):
            circ.measure(i,i)
        return circ

# 적당한 Cliford circuit
class example_circuit_2:

    def __init__(self) -> None:
        self.num_qubit = 30
    
    def function(self, circ):
        for i in range(0, self.num_qubit-1, 2):
            circ.h(i)
            circ.cx(i, i+1)
        
        for i in range(1, self.num_qubit-2, 2):
            circ.s(i)
            circ.cx(i, i+1)
        for i in range(self.num_qubit):
            circ.measure(i,i)
        return circ




