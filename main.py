from sampler import simulation_sampler
from circuits import example_circuit, GHZ_circuit
import time



def main():
    circuit_fun = GHZ_circuit
    num_qubit = 100
    num_shot = int(1e4)
    qiskit_result = simulation_sampler(circuit_fun, 'qiskit', num_qubit, num_shot ).get_result()
    clifford_result = simulation_sampler(circuit_fun, 'clifford', num_qubit, num_shot).get_result()

    print(clifford_result)
    print(qiskit_result)






if __name__ == '__main__':
    main()








