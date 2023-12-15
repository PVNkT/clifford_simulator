from sampler import simulation_sampler
from circuits import example_circuit, example_circuit_2, GHZ_circuit
import time



def main():
    circuit_fun = example_circuit()
    num_shot = int(1e4)
    qiskit_sampler = simulation_sampler(circuit_fun, 'qiskit', num_shot )
    qiskit_result = qiskit_sampler.get_result()
    clifford_result = simulation_sampler(circuit_fun, 'clifford', num_shot).get_result()
    print(clifford_result)
    print(qiskit_result)
    qiskit_sampler.circuit.draw()





if __name__ == '__main__':
    main()








