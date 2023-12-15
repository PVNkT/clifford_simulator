from qiskit import QuantumCircuit

from qiskit_aer.primitives import Sampler
from clifford_circuit import clifford_simulator

class simulation_sampler:
    """
    Clifford simulator와 qiskit simulator에 대해서 measurement sampling을 진행
    """
    def __init__(self, circuit_class, simulator_name, shot):
        self.n = circuit_class.num_qubit
        self.circuit_fun = circuit_class.function
        self.circ = getattr(self, simulator_name+'_simulation')
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
        result_dict = {key: value / shot for key, value in result_dic.items()}

        return result_dict
    
    # qiskit을 사용한 sampling
    def qiskit_sampler(self, shot):
        sampler = Sampler()
        self.circuit = self.circuit_fun(circ = self.circ())
        result_dic = sampler.run(self.circuit, shot=shot).result().quasi_dists[0].binary_probabilities()
        return result_dic

    def get_result(self):
        return dict(self.result)




if __name__ == '__main__':
    from circuits import example_circuit
    result = simulation_sampler(example_circuit, 'qiskit', 3, 10000).get_result()
    print(result)












