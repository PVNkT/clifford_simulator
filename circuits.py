


def example_circuit(circ):
    
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

    return circ


def GHZ_circuit(circ):
    circ.h(0)
    for i in range(99):
        circ.cx(i,i+1)
    for i in range(100):
        circ.measure(i,i)
    return circ