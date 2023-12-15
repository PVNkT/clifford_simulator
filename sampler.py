from qiskit import QuantumCircuit

from qiskit_aer.primitives import Sampler
from clifford_circuit import clifford_simulator

class simulation_sampler:

    def __init__(self, circuit_fun, simulator_name, num_qubit, shot):
        self.n = num_qubit
        self.circ = getattr(self, simulator_name+'_simulation')
        self.circuit_fun = circuit_fun
        self.result = getattr(self, simulator_name+'_sampler')(shot)

    def clifford_simulation(self):
        circ = clifford_simulator(self.n)
        return circ

    def qiskit_simulation(self):
        circ = QuantumCircuit(self.n, self.n)
        return circ

    def clifford_sampler(self, shot):
        result_dic = {}
        for _ in range(shot):
            circuit = self.circuit_fun(circ = self.circ())
            result = circuit.get_sampling_result()
            try:
                result_dic[str(result)] += 1
            except:
                result_dic[str(result)] = 1
        
        return result_dic
    
    def qiskit_sampler(self, shot):
        sampler = Sampler()
        circuit = self.circuit_fun(circ = self.circ())
        result_dic = sampler.run(circuit, shot=shot).result().quasi_dists[0]
        return result_dic

    def get_result(self):
        return dict(self.result)




if __name__ == '__main__':
    from circuits import example_circuit
    result = simulation_sampler(example_circuit, 'qiskit', 3, 10000).get_result()
    print(result)












